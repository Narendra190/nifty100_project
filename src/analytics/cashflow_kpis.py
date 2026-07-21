import os
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd


def free_cash_flow(operating_activity, investing_activity):
    return operating_activity + investing_activity


def cfo_quality_score(cfo_list, pat_list):
    ratios = []

    for cfo, pat in zip(cfo_list, pat_list):
        if pat == 0:
            continue
        ratios.append(cfo / pat)

    if len(ratios) == 0:
        return None

    avg_ratio = sum(ratios) / len(ratios)

    if avg_ratio > 1:
        return "High Quality"

    elif avg_ratio >= 0.5:
        return "Moderate"

    else:
        return "Accrual Risk"


def capex_intensity(investing_activity, sales):
    if sales == 0:
        return None

    intensity = abs(investing_activity) / sales * 100

    if intensity < 3:
        label = "Asset Light"

    elif intensity <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


def fcf_conversion_rate(fcf, operating_profit):
    if operating_profit == 0:
        return None

    return (fcf / operating_profit) * 100


def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=1):

    cfo_sign = "+" if cfo >= 0 else "-"
    cfi_sign = "+" if cfi >= 0 else "-"
    cff_sign = "+" if cff >= 0 else "-"

    signs = (cfo_sign, cfi_sign, cff_sign)

    mapping = {
        ("+", "-", "-"): "Shareholder Returns" if cfo_pat_ratio > 1 else "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    if signs == ("-", "-", "+"):
        return cfo_sign, cfi_sign, cff_sign, "Growth Funded by Debt"
    if signs == ("-", "+", "+"):
        return cfo_sign, cfi_sign, cff_sign, "Distress Signal"

    return (
        cfo_sign,
        cfi_sign,
        cff_sign,
        mapping.get(signs, "Unknown")
    )


def export_capital_allocation(df, output_file="output/capital_allocation.csv"):
    df.to_csv(output_file, index=False)


def _normalize_year_label(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""

    if len(text) >= 4 and text[-4:].isdigit():
        return text[-4:]

    import re
    match = re.search(r'(\d{4})', text)
    if match:
        return match.group(1)

    match = re.search(r'(\d{2})', text)
    if match:
        year_value = int(match.group(1))
        return str(2000 + year_value if year_value < 100 else year_value)

    try:
        return str(pd.to_datetime(text, errors='coerce').year)
    except Exception:
        return text


def summarize_pattern_distribution(report: pd.DataFrame, latest_year: Optional[str] = None) -> dict:
    if report.empty:
        return {}

    report = report.copy()
    report["year"] = report["year"].apply(_normalize_year_label)

    if latest_year is None:
        latest_year = str(report["year"].max())

    latest = report[report["year"] == latest_year]
    if latest.empty:
        latest = report.sort_values("year").groupby("company_id").tail(1).reset_index(drop=True)

    latest = latest.drop_duplicates(subset=["company_id"])

    patterns = [
        "Reinvestor",
        "Shareholder Returns",
        "Liquidating Assets",
        "Distress Signal",
        "Growth Funded by Debt",
        "Cash Accumulator",
        "Pre-Revenue",
        "Mixed",
    ]

    summary = {pattern: 0 for pattern in patterns}
    for pattern in latest["pattern_label"].dropna().tolist():
        summary[pattern] = summary.get(pattern, 0) + 1
    return summary


def build_pattern_change_report(report: pd.DataFrame) -> pd.DataFrame:
    if report.empty:
        return pd.DataFrame(columns=["company_id", "year_from", "year_to", "pattern_from", "pattern_to", "change_summary"])

    report = report.copy()
    report["year"] = report["year"].apply(_normalize_year_label)
    report = report.sort_values(["company_id", "year"]).reset_index(drop=True)

    changes = []
    for company_id, company_rows in report.groupby("company_id"):
        if len(company_rows) < 2:
            continue

        for idx in range(1, len(company_rows)):
            previous = company_rows.iloc[idx - 1]
            current = company_rows.iloc[idx]
            if previous.get("pattern_label") != current.get("pattern_label"):
                change_summary = f"{company_id}: {previous.get('pattern_label')} -> {current.get('pattern_label')} ({previous['year']} to {current['year']})"
                changes.append({
                    "company_id": company_id,
                    "year_from": previous["year"],
                    "year_to": current["year"],
                    "pattern_from": previous.get("pattern_label"),
                    "pattern_to": current.get("pattern_label"),
                    "change_summary": change_summary,
                })

    return pd.DataFrame(changes)


def build_capital_allocation_report(
    cashflow_df: pd.DataFrame,
    company_ids: Optional[list] = None,
    years: Optional[list] = None,
    profit_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    if cashflow_df.empty:
        return pd.DataFrame(columns=["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"])

    cashflow_df = cashflow_df.copy()
    cashflow_df["company_id"] = cashflow_df["company_id"].astype(str)
    cashflow_df["year"] = cashflow_df["year"].apply(_normalize_year_label)

    if company_ids is None:
        company_ids = sorted(set(cashflow_df["company_id"]))
    else:
        company_ids = [str(item) for item in company_ids]

    if years is None:
        years = sorted(set(cashflow_df["year"]))
    else:
        years = [str(_normalize_year_label(item)) for item in years]

    if profit_df is not None:
        profit_df = profit_df.copy()
        profit_df["company_id"] = profit_df["company_id"].astype(str)
        profit_df["year"] = profit_df["year"].apply(_normalize_year_label)

    rows = []
    for company_id in company_ids:
        for year in years:
            row = cashflow_df[(cashflow_df["company_id"] == company_id) & (cashflow_df["year"] == year)]
            if row.empty:
                cfo = None
                cfi = None
                cff = None
                pattern_label = "Unknown"
                cfo_sign = "?"
                cfi_sign = "?"
                cff_sign = "?"
            else:
                values = row.iloc[0]
                cfo = _safe_numeric(values.get("operating_activity"))
                cfi = _safe_numeric(values.get("investing_activity"))
                cff = _safe_numeric(values.get("financing_activity"))

                profit_row = None
                if profit_df is not None:
                    profit_matches = profit_df[(profit_df["company_id"] == company_id) & (profit_df["year"] == year)]
                    if not profit_matches.empty:
                        profit_row = profit_matches.iloc[0]

                cfo_pat_ratio = 1
                if profit_row is not None:
                    pat = _safe_numeric(profit_row.get("net_profit"))
                    if pat not in [None, 0]:
                        cfo_pat_ratio = (cfo / pat) if cfo is not None else 1

                cfo_sign, cfi_sign, cff_sign, pattern_label = capital_allocation_pattern(
                    cfo=cfo if cfo is not None else 0,
                    cfi=cfi if cfi is not None else 0,
                    cff=cff if cff is not None else 0,
                    cfo_pat_ratio=cfo_pat_ratio,
                )

            rows.append({
                "company_id": company_id,
                "year": year,
                "cfo_sign": cfo_sign,
                "cfi_sign": cfi_sign,
                "cff_sign": cff_sign,
                "pattern_label": pattern_label,
            })

    report = pd.DataFrame(rows)
    if not report.empty:
        report["year"] = report["year"].astype(str)
        report = report.sort_values(["company_id", "year"]).reset_index(drop=True)
    return report


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _cfo_quality_label(score: Optional[float]) -> str:
    if score is None:
        return "Unknown"
    if score > 1.0:
        return "High Quality"
    if score >= 0.5:
        return "Moderate"
    return "Accrual Risk"


def _capex_label(intensity_pct: Optional[float]) -> str:
    if intensity_pct is None:
        return "Unknown"
    if intensity_pct < 3:
        return "Asset Light"
    if intensity_pct <= 8:
        return "Moderate"
    return "Capital Intensive"


def _fcf_cagr(values):
    values = [v for v in values if v is not None and not isinstance(v, complex)]
    values = [float(v) for v in values if isinstance(v, (int, float)) or str(v).replace('.', '', 1).lstrip('-').isdigit()]
    if len(values) < 2:
        return None
    start = values[0]
    end = values[-1]
    if start == 0:
        return None
    try:
        return ((end / start) ** (1 / (len(values) - 1)) - 1) * 100
    except (OverflowError, ZeroDivisionError, ValueError):
        return None


def generate_cashflow_intelligence(
    db_path: Optional[str] = None,
    output_xlsx: Optional[str] = None,
    distress_csv: Optional[str] = None,
) -> pd.DataFrame:
    root = _project_root()
    db_file = Path(db_path) if db_path else root / "nifty100.db"
    xlsx_path = Path(output_xlsx) if output_xlsx else root / "output" / "cashflow_intelligence.xlsx"
    alerts_path = Path(distress_csv) if distress_csv else root / "output" / "distress_alerts.csv"

    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file}")

    conn = sqlite3.connect(db_file)
    try:
        cashflow = pd.read_sql_query("SELECT * FROM cashflow_clean", conn)
        profit = pd.read_sql_query("SELECT * FROM profitandloss_clean", conn)
        balance = pd.read_sql_query("SELECT * FROM balancesheet_clean", conn)
        companies = pd.read_sql_query("SELECT * FROM companies_clean", conn)
        sectors = pd.read_sql_query("SELECT * FROM sectors_clean", conn)
    finally:
        conn.close()

    if cashflow.empty or profit.empty:
        raise ValueError("Cash flow and profit data are required to generate intelligence")

    cashflow = cashflow.copy()
    profit = profit.copy()
    balance = balance.copy()
    companies = companies.copy()
    sectors = sectors.copy()

    for frame in [cashflow, profit, balance, companies]:
        for column in ["company_id", "year"]:
            if column in frame.columns:
                frame[column] = frame[column].astype(str)

    rows = []
    distress_rows = []

    for company_id in sorted(set(cashflow["company_id"]).union(set(profit["company_id"]))):
        cfs = cashflow[cashflow["company_id"] == company_id].copy()
        pl = profit[profit["company_id"] == company_id].copy()
        bal = balance[balance["company_id"] == company_id].copy()

        if cfs.empty or pl.empty:
            continue

        cfs = cfs.sort_values("year")
        pl = pl.sort_values("year")
        bal = bal.sort_values("year")

        latest_cfs = cfs.iloc[-1]
        latest_pl = pl.iloc[-1]

        cfo_values = []
        pat_values = []
        fcf_values = []
        sales_values = []
        cff_values = []
        borrowings_values = []

        for _, row in cfs.iterrows():
            cfo_values.append(_safe_numeric(row.get("operating_activity")))
            cff_values.append(_safe_numeric(row.get("financing_activity")))
            fcf_values.append(_safe_numeric(row.get("operating_activity")) + _safe_numeric(row.get("investing_activity")))

        for _, row in pl.iterrows():
            pat_values.append(_safe_numeric(row.get("net_profit")))
            sales_values.append(_safe_numeric(row.get("sales")))

        ratios = []
        for cfo, pat in zip(cfo_values, pat_values):
            if pat is None or pat == 0:
                continue
            ratios.append(cfo / pat)
        avg_ratio = sum(ratios) / len(ratios) if ratios else None

        latest_sales = _safe_numeric(latest_pl.get("sales"))
        latest_investing = _safe_numeric(latest_cfs.get("investing_activity"))
        capex_intensity_pct = None if latest_sales in [None, 0] else abs(latest_investing) / latest_sales * 100

        latest_cfo = _safe_numeric(latest_cfs.get("operating_activity"))
        latest_cff = _safe_numeric(latest_cfs.get("financing_activity"))
        latest_net_profit = _safe_numeric(latest_pl.get("net_profit"))
        latest_borrowings = _safe_numeric(bal.iloc[-1].get("borrowings")) if not bal.empty else None
        prev_borrowings = _safe_numeric(bal.iloc[-2].get("borrowings")) if len(bal) >= 2 else None

        distress_flag = bool(latest_cfo is not None and latest_cff is not None and latest_cfo < 0 and latest_cff > 0)
        deleveraging_flag = bool(latest_cff is not None and latest_borrowings is not None and prev_borrowings is not None and latest_cff < 0 and latest_borrowings < prev_borrowings)

        capital_allocation_label = "Unknown"
        if distress_flag:
            capital_allocation_label = "Distress Signal"
        elif deleveraging_flag:
            capital_allocation_label = "Deleveraging"
        else:
            capital_allocation_label = "Balanced"

        sector = ""
        if not companies.empty:
            meta = companies[companies["company_id"] == company_id]
            if not meta.empty:
                sector = str(meta.iloc[0].get("sector", ""))
        if not sectors.empty and not sector:
            sector_row = sectors[sectors["company_id"] == company_id]
            if not sector_row.empty:
                sector = str(sector_row.iloc[0].get("sector_name", ""))

        fcf_cagr_value = _fcf_cagr(fcf_values[-5:])
        if isinstance(fcf_cagr_value, complex):
            fcf_cagr_value = None
        fcf_conversion_value = None
        if latest_pl.get("operating_profit") not in [None, 0]:
            fcf_conversion_value = ((latest_cfo + latest_investing) / latest_pl.get("operating_profit", 0) * 100) if latest_cfo is not None and latest_investing is not None else None

        rows.append({
            "company_id": company_id,
            "sector": sector,
            "cfo_quality_score": round(avg_ratio, 2) if avg_ratio is not None else None,
            "cfo_quality_label": _cfo_quality_label(avg_ratio),
            "capex_intensity_pct": round(capex_intensity_pct, 2) if capex_intensity_pct is not None else None,
            "capex_label": _capex_label(capex_intensity_pct),
            "fcf_cagr_5yr": round(fcf_cagr_value, 2) if fcf_cagr_value is not None else None,
            "fcf_conversion_pct": round(fcf_conversion_value, 2) if fcf_conversion_value is not None else None,
            "distress_flag": distress_flag,
            "deleveraging_flag": deleveraging_flag,
            "capital_allocation_label": capital_allocation_label,
        })

        if distress_flag:
            distress_rows.append({
                "company_id": company_id,
                "sector": sector,
                "cfo": latest_cfo,
                "cff": latest_cff,
                "latest_net_profit": latest_net_profit,
            })

    result = pd.DataFrame(rows)
    result = result[[
        "company_id",
        "sector",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_intensity_pct",
        "capex_label",
        "fcf_cagr_5yr",
        "fcf_conversion_pct",
        "distress_flag",
        "deleveraging_flag",
        "capital_allocation_label",
    ]]

    xlsx_path.parent.mkdir(parents=True, exist_ok=True)
    alerts_path.parent.mkdir(parents=True, exist_ok=True)

    cashflow_report = build_capital_allocation_report(
        cashflow_df=cashflow,
        company_ids=sorted(set(companies["company_id"])),
        years=sorted(set(cashflow["year"]).union(set(profit["year"])).union(set(balance["year"]))),
        profit_df=profit,
    )
    capital_output_path = root / "output" / "capital_allocation.csv"
    export_capital_allocation(cashflow_report, output_file=str(capital_output_path))

    latest_year = None
    if not cashflow_report.empty:
        valid_years = [str(y) for y in cashflow_report["year"].dropna().astype(str) if str(y).strip() and str(y).strip() != "nan"]
        if valid_years:
            latest_year = sorted(valid_years)[-1]
    distribution_summary = summarize_pattern_distribution(cashflow_report, latest_year=latest_year)
    distribution_df = pd.DataFrame(
        [{"latest_year": latest_year, **distribution_summary}]
    )
    distribution_df.to_csv(root / "output" / "pattern_distribution_latest_year.csv", index=False)

    pattern_changes = build_pattern_change_report(cashflow_report)
    pattern_changes.to_csv(root / "output" / "pattern_changes.csv", index=False)

    latest_patterns = cashflow_report.sort_values(["company_id", "year"]).drop_duplicates(subset=["company_id"], keep="last")
    latest_patterns_map = latest_patterns.set_index("company_id")["pattern_label"]
    result["capital_allocation_pattern"] = result["company_id"].map(latest_patterns_map)
    result.to_excel(xlsx_path, index=False)

    distress_df = pd.DataFrame(distress_rows)
    if not distress_df.empty:
        distress_df.to_csv(alerts_path, index=False)
    else:
        distress_df.to_csv(alerts_path, index=False)

    return result
