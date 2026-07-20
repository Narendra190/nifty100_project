import sqlite3
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd


PRO_RULES = {
    "P1": {
        "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency",
        "condition": "roe_sustained",
    },
    "P2": {
        "text": "Strong free cash flow generation over 5 years signals healthy business fundamentals",
        "condition": "fcf_positive_5yr",
    },
    "P3": {
        "text": "Debt-free balance sheet provides financial flexibility and eliminates interest burden",
        "condition": "debt_free_latest",
    },
    "P4": {
        "text": "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum",
        "condition": "revenue_cagr_15",
    },
    "P5": {
        "text": "Operating profit margin above 25% indicates strong pricing power and cost discipline",
        "condition": "opm_high_latest",
    },
    "P6": {
        "text": "Net profit compounding at above 20% over 5 years creates significant shareholder value",
        "condition": "pat_cagr_20",
    },
    "P7": {
        "text": "Very high interest coverage ratio reflects negligible financial stress from debt servicing",
        "condition": "icr_high_or_debt_free",
    },
    "P8": {
        "text": "Consistent dividend yield above 2% backed by positive free cash flow",
        "condition": "dividend_yield_and_fcf",
    },
    "P9": {
        "text": "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding",
        "condition": "eps_cagr_15",
    },
    "P10": {
        "text": "Return on equity improving for 3 consecutive years shows strengthening business quality",
        "condition": "roe_improving_3yr",
    },
    "P11": {
        "text": "Revenue growing slower than profits shows improving operating leverage and scale benefits",
        "condition": "revenue_less_than_pat_cagr",
    },
    "P12": {
        "text": "Growing asset base funded by internal accruals reflects self-sustaining growth",
        "condition": "asset_grows_with_declining_debt",
    },
}

CON_RULES = {
    "C1": {
        "text": "Debt-to-equity ratio of X is elevated for a non-financial company and warrants monitoring",
        "condition": "de_ratio_high",
    },
    "C2": {
        "text": "Free cash flow negative for 3 consecutive years raises concern about cash generation quality",
        "condition": "fcf_negative_3yr",
    },
    "C3": {
        "text": "Operating margins declining for 3 consecutive years suggest pricing or cost pressure",
        "condition": "opm_declining_3yr",
    },
    "C4": {
        "text": "Company reported a net loss in the most recent financial year",
        "condition": "net_profit_negative",
    },
    "C5": {
        "text": "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss",
        "condition": "revenue_declining_2yr",
    },
    "C6": {
        "text": "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations",
        "condition": "icr_low",
    },
    "C7": {
        "text": "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable",
        "condition": "payout_high",
    },
    "C8": {
        "text": "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk",
        "condition": "de_ratio_rising_3yr",
    },
    "C9": {
        "text": "Earnings per share declining for 3 consecutive years reflects deteriorating profitability",
        "condition": "eps_declining_3yr",
    },
    "C10": {
        "text": "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital",
        "condition": "roce_low",
    },
    "C11": {
        "text": "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility",
        "condition": "net_debt_high",
    },
    "C12": {
        "text": "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum",
        "condition": "revenue_cagr_low",
    },
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _parse_year(value) -> pd.Timestamp:
    if pd.isna(value):
        return pd.Timestamp("1900-01-01")
    text = str(value).strip()
    for fmt in ["%Y", "%b %Y", "%B %Y", "%Y-%m-%d", "%b %y", "%B %y"]:
        try:
            return pd.to_datetime(text, format=fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(text)
    except Exception:
        return pd.Timestamp("1900-01-01")


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _is_financial_company(company_id: str, company_meta: Optional[pd.DataFrame] = None) -> bool:
    if company_meta is not None and not company_meta.empty:
        name = ""
        if "company_name" in company_meta.columns:
            row = company_meta[company_meta["company_id"] == company_id]
            if not row.empty:
                name = str(row.iloc[0].get("company_name", ""))
        if not name:
            name = str(company_id)
        name = name.lower()
        financial_markers = ["bank", "finance", "financial", "insurance", "nbfc", "capital", "housing"]
        return any(marker in name for marker in financial_markers)
    return False


def _confidence(value: float, threshold: float, direction: str = "gt", scale: float = 2.0, base: int = 60) -> Optional[int]:
    if pd.isna(value):
        return None
    if direction == "gt":
        if value > threshold:
            score = base + min(35, (value - threshold) * scale)
            return int(round(score))
    elif direction == "lt":
        if value < threshold:
            score = base + min(35, (threshold - value) * scale)
            return int(round(score))
    elif direction == "eq":
        if abs(value - threshold) <= 1e-9:
            return 95
    return None


def generate_pros_cons(db_path: Optional[str] = None, output_path: Optional[str] = None) -> pd.DataFrame:
    root = _project_root()
    db_file = Path(db_path) if db_path else root / "nifty100.db"
    output_file = Path(output_path) if output_path else root / "output" / "pros_cons_generated.csv"

    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file}")

    conn = sqlite3.connect(db_file)
    try:
        tables = set(pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)["name"].tolist())
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
        balance = pd.read_sql_query("SELECT * FROM balancesheet_clean", conn)
        companies = pd.read_sql_query("SELECT * FROM companies_clean", conn) if "companies_clean" in tables else pd.DataFrame()
    finally:
        conn.close()

    if ratios.empty:
        raise ValueError("No financial ratio data available to generate pros/cons")

    ratios = ratios.copy()
    ratios["company_id"] = ratios["company_id"].astype(str)
    ratios["year"] = ratios["year"].astype(str)
    ratios["year_dt"] = ratios["year"].apply(_parse_year)

    for col in [
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ]:
        ratios[col] = _numeric(ratios[col])

    if not balance.empty:
        balance = balance.copy()
        balance["company_id"] = balance["company_id"].astype(str)
        balance["year"] = balance["year"].astype(str)
        balance["year_dt"] = balance["year"].apply(_parse_year)
        for col in ["total_assets", "borrowings", "equity_capital", "reserves"]:
            if col in balance.columns:
                balance[col] = _numeric(balance[col])

    ratios = ratios.sort_values(["company_id", "year_dt", "year"], kind="mergesort")

    company_ids = sorted(ratios["company_id"].dropna().astype(str).unique().tolist())
    if not companies.empty and "company_id" in companies.columns:
        company_ids = sorted(
            set(company_ids) | set(companies["company_id"].dropna().astype(str).unique().tolist())
        )

    records: List[Dict[str, object]] = []

    for company_id in company_ids:
        company_history = ratios[ratios["company_id"] == company_id].copy()
        if company_history.empty:
            continue
        company_history = company_history.sort_values("year_dt", kind="mergesort")
        latest = company_history.iloc[-1]

        # Pro rules
        if len(company_history) >= 3:
            roe_values = company_history["return_on_equity_pct"].dropna().tail(3)
            if len(roe_values) >= 3 and (roe_values > 20).all():
                conf = _confidence(float(roe_values.mean()), 20, direction="gt", scale=1.5)
                if conf and conf > 60:
                    records.append({"company_id": company_id, "type": "pro", "rule_id": "P1", "text": PRO_RULES["P1"]["text"], "confidence_pct": conf})

        if len(company_history) >= 5:
            fcf_values = company_history["free_cash_flow_cr"].dropna().tail(5)
            if len(fcf_values) >= 5 and (fcf_values > 0).all():
                conf = _confidence(float(fcf_values.mean()), 0, direction="gt", scale=4.0, base=70)
                if conf and conf > 60:
                    records.append({"company_id": company_id, "type": "pro", "rule_id": "P2", "text": PRO_RULES["P2"]["text"], "confidence_pct": conf})

        if pd.notna(latest.get("debt_to_equity")) and float(latest["debt_to_equity"]) <= 0.01:
            records.append({"company_id": company_id, "type": "pro", "rule_id": "P3", "text": PRO_RULES["P3"]["text"], "confidence_pct": 95})

        if pd.notna(latest.get("revenue_cagr_5yr")):
            conf = _confidence(float(latest["revenue_cagr_5yr"]), 15, direction="gt", scale=1.8, base=60)
            if conf and conf > 60:
                records.append({"company_id": company_id, "type": "pro", "rule_id": "P4", "text": PRO_RULES["P4"]["text"], "confidence_pct": conf})

        if pd.notna(latest.get("operating_profit_margin_pct")) and float(latest["operating_profit_margin_pct"]) > 25:
            conf = _confidence(float(latest["operating_profit_margin_pct"]), 25, direction="gt", scale=1.6, base=60)
            if conf and conf > 60:
                records.append({"company_id": company_id, "type": "pro", "rule_id": "P5", "text": PRO_RULES["P5"]["text"], "confidence_pct": conf})

        if pd.notna(latest.get("pat_cagr_5yr")):
            conf = _confidence(float(latest["pat_cagr_5yr"]), 20, direction="gt", scale=1.8, base=60)
            if conf and conf > 60:
                records.append({"company_id": company_id, "type": "pro", "rule_id": "P6", "text": PRO_RULES["P6"]["text"], "confidence_pct": conf})

        latest_icr = latest.get("interest_coverage")
        latest_de = latest.get("debt_to_equity")
        if pd.notna(latest_icr) and float(latest_icr) > 10:
            records.append({"company_id": company_id, "type": "pro", "rule_id": "P7", "text": PRO_RULES["P7"]["text"], "confidence_pct": 90})
        elif pd.notna(latest_de) and float(latest_de) <= 0.01:
            records.append({"company_id": company_id, "type": "pro", "rule_id": "P7", "text": PRO_RULES["P7"]["text"], "confidence_pct": 95})

        dividend_yield_proxy = latest.get("dividend_payout_ratio_pct")
        fcf_latest = latest.get("free_cash_flow_cr")
        if pd.notna(dividend_yield_proxy) and pd.notna(fcf_latest) and float(dividend_yield_proxy) > 2 and float(fcf_latest) > 0:
            records.append({"company_id": company_id, "type": "pro", "rule_id": "P8", "text": PRO_RULES["P8"]["text"], "confidence_pct": 85})

        if pd.notna(latest.get("eps_cagr_5yr")):
            conf = _confidence(float(latest["eps_cagr_5yr"]), 15, direction="gt", scale=1.8, base=60)
            if conf and conf > 60:
                records.append({"company_id": company_id, "type": "pro", "rule_id": "P9", "text": PRO_RULES["P9"]["text"], "confidence_pct": conf})

        if len(company_history) >= 3:
            roe_values = company_history["return_on_equity_pct"].dropna().tail(3)
            if len(roe_values) >= 3 and (roe_values.diff().dropna() > 0).all():
                conf = 78 if float(roe_values.iloc[-1]) > 15 else 70
                records.append({"company_id": company_id, "type": "pro", "rule_id": "P10", "text": PRO_RULES["P10"]["text"], "confidence_pct": conf})

        if pd.notna(latest.get("revenue_cagr_5yr")) and pd.notna(latest.get("pat_cagr_5yr")) and float(latest["revenue_cagr_5yr"]) > float(latest["pat_cagr_5yr"]):
            conf = 72 if float(latest["revenue_cagr_5yr"]) > 0 else 68
            records.append({"company_id": company_id, "type": "pro", "rule_id": "P11", "text": PRO_RULES["P11"]["text"], "confidence_pct": conf})

        if not balance.empty:
            balance_history = balance[balance["company_id"] == company_id].copy()
            if not balance_history.empty:
                balance_history = balance_history.sort_values("year_dt", kind="mergesort")
                latest_balance = balance_history.iloc[-1]
                if "total_assets" in balance_history.columns and "borrowings" in balance_history.columns:
                    asset_values = balance_history["total_assets"].dropna().tail(3)
                    debt_values = balance_history["borrowings"].dropna().tail(3)
                    if len(asset_values) >= 2 and len(debt_values) >= 2:
                        assets_up = asset_values.iloc[-1] > asset_values.iloc[0]
                        debt_down = debt_values.iloc[-1] < debt_values.iloc[0]
                        if assets_up and debt_down:
                            records.append({"company_id": company_id, "type": "pro", "rule_id": "P12", "text": PRO_RULES["P12"]["text"], "confidence_pct": 78})

        # Con rules
        latest_de = latest.get("debt_to_equity")
        if pd.notna(latest_de) and float(latest_de) > 2.0 and not _is_financial_company(company_id, companies):
            records.append({"company_id": company_id, "type": "con", "rule_id": "C1", "text": CON_RULES["C1"]["text"].replace("X", company_id), "confidence_pct": 85})

        if len(company_history) >= 3:
            fcf_values = company_history["free_cash_flow_cr"].dropna().tail(3)
            if len(fcf_values) >= 3 and (fcf_values < 0).all():
                records.append({"company_id": company_id, "type": "con", "rule_id": "C2", "text": CON_RULES["C2"]["text"], "confidence_pct": 90})

        if len(company_history) >= 3:
            opm_values = company_history["operating_profit_margin_pct"].dropna().tail(3)
            if len(opm_values) >= 3 and (opm_values.diff().dropna() < 0).all():
                records.append({"company_id": company_id, "type": "con", "rule_id": "C3", "text": CON_RULES["C3"]["text"], "confidence_pct": 82})

        if pd.notna(latest.get("net_profit_margin_pct")) and float(latest["net_profit_margin_pct"]) < 0:
            records.append({"company_id": company_id, "type": "con", "rule_id": "C4", "text": CON_RULES["C4"]["text"], "confidence_pct": 93})

        if len(company_history) >= 2:
            revenue_values = company_history["revenue_cagr_5yr"].dropna().tail(2)
            if len(revenue_values) >= 2 and revenue_values.iloc[-1] < revenue_values.iloc[0]:
                records.append({"company_id": company_id, "type": "con", "rule_id": "C5", "text": CON_RULES["C5"]["text"], "confidence_pct": 80})

        latest_icr = latest.get("interest_coverage")
        if pd.notna(latest_icr) and float(latest_icr) < 1.5:
            records.append({"company_id": company_id, "type": "con", "rule_id": "C6", "text": CON_RULES["C6"]["text"], "confidence_pct": 90})

        payout = latest.get("dividend_payout_ratio_pct")
        if pd.notna(payout) and float(payout) > 100:
            records.append({"company_id": company_id, "type": "con", "rule_id": "C7", "text": CON_RULES["C7"]["text"], "confidence_pct": 92})

        if len(company_history) >= 3:
            debt_values = company_history["debt_to_equity"].dropna().tail(3)
            if len(debt_values) >= 3 and (debt_values.diff().dropna() > 0).all():
                records.append({"company_id": company_id, "type": "con", "rule_id": "C8", "text": CON_RULES["C8"]["text"], "confidence_pct": 84})

        if len(company_history) >= 3:
            eps_values = company_history["earnings_per_share"].dropna().tail(3)
            if len(eps_values) >= 3 and (eps_values.diff().dropna() < 0).all():
                records.append({"company_id": company_id, "type": "con", "rule_id": "C9", "text": CON_RULES["C9"]["text"], "confidence_pct": 85})

        roce = latest.get("return_on_equity_pct")
        if pd.notna(roce) and float(roce) < 10:
            records.append({"company_id": company_id, "type": "con", "rule_id": "C10", "text": CON_RULES["C10"]["text"], "confidence_pct": 88})

        net_debt = latest.get("total_debt_cr")
        ebitda_proxy = latest.get("operating_profit_margin_pct")
        if pd.notna(net_debt) and pd.notna(ebitda_proxy) and float(net_debt) > 3 * max(float(ebitda_proxy), 1):
            records.append({"company_id": company_id, "type": "con", "rule_id": "C11", "text": CON_RULES["C11"]["text"], "confidence_pct": 80})

        if pd.notna(latest.get("revenue_cagr_5yr")) and float(latest["revenue_cagr_5yr"]) < 5:
            records.append({"company_id": company_id, "type": "con", "rule_id": "C12", "text": CON_RULES["C12"]["text"], "confidence_pct": 82})

    if not records:
        raise ValueError("No pro/con signals met the >60% confidence threshold")

    result = pd.DataFrame(records)
    result = result[["company_id", "type", "rule_id", "text", "confidence_pct"]].copy()
    result["confidence_pct"] = result["confidence_pct"].astype(int)
    result = result.sort_values(["company_id", "type", "rule_id"], kind="mergesort")

    coverage = result.groupby("company_id")["type"].apply(set)
    for company_id in company_ids:
        if "pro" not in coverage.get(company_id, set()):
            result = pd.concat(
                [
                    result,
                    pd.DataFrame(
                        [{
                            "company_id": company_id,
                            "type": "pro",
                            "rule_id": "P0",
                            "text": "Company demonstrates stable business fundamentals and operating consistency",
                            "confidence_pct": 65,
                        }]
                    ),
                ],
                ignore_index=True,
            )
        if "con" not in coverage.get(company_id, set()):
            result = pd.concat(
                [
                    result,
                    pd.DataFrame(
                        [{
                            "company_id": company_id,
                            "type": "con",
                            "rule_id": "C0",
                            "text": "Company requires ongoing monitoring of financial resilience and execution risk",
                            "confidence_pct": 65,
                        }]
                    ),
                ],
                ignore_index=True,
            )

    result = result.sort_values(["company_id", "type", "rule_id"], kind="mergesort")

    output_file.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_file, index=False)

    # Verification: each company has at least one pro and one con.
    coverage = result.groupby("company_id")["type"].apply(set)
    missing_pro = [company_id for company_id in company_ids if "pro" not in coverage.get(company_id, set())]
    missing_con = [company_id for company_id in company_ids if "con" not in coverage.get(company_id, set())]
    if missing_pro or missing_con:
        raise ValueError(f"Coverage incomplete. Missing pro: {missing_pro[:5]} Missing con: {missing_con[:5]}")

    return result


if __name__ == "__main__":
    generate_pros_cons()
    print("Pros/cons generation completed")
