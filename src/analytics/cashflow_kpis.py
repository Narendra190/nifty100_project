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

    return (
        cfo_sign,
        cfi_sign,
        cff_sign,
        mapping.get(signs, "Unknown")
    )


def export_capital_allocation(df, output_file="output/capital_allocation.csv"):
    df.to_csv(output_file, index=False)


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
    result.to_excel(xlsx_path, index=False)
    distress_df = pd.DataFrame(distress_rows)
    if not distress_df.empty:
        distress_df.to_csv(alerts_path, index=False)
    else:
        distress_df.to_csv(alerts_path, index=False)

    return result
