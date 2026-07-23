import io
import sqlite3
from pathlib import Path
from typing import Optional, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak, KeepTogether, Image
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import LineChart
from reportlab.graphics.widgets.markers import makeMarker


PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.5 * inch


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


def _load_company_data(db_path: Optional[str] = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    root = _project_root()
    db_file = Path(db_path) if db_path else root / "nifty100.db"
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file}")

    conn = sqlite3.connect(db_file)
    try:
        companies = pd.read_sql_query("SELECT * FROM companies_clean", conn)
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
        cashflow = pd.read_sql_query("SELECT * FROM cashflow_clean", conn)
        balance = pd.read_sql_query("SELECT * FROM balancesheet_clean", conn)
    finally:
        conn.close()

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
        if col in ratios.columns:
            ratios[col] = _numeric(ratios[col])

    balance = balance.copy()
    balance["company_id"] = balance["company_id"].astype(str)
    balance["year"] = balance["year"].astype(str)
    balance["year_dt"] = balance["year"].apply(_parse_year)
    for col in ["total_assets", "borrowings", "equity_capital", "reserves", "other_liabilities"]:
        if col in balance.columns:
            balance[col] = _numeric(balance[col])

    cashflow = cashflow.copy()
    cashflow["company_id"] = cashflow["company_id"].astype(str)
    cashflow["year"] = cashflow["year"].astype(str)
    cashflow["year_dt"] = cashflow["year"].apply(_parse_year)
    for col in ["operating_activity", "investing_activity", "financing_activity", "net_cash_flow"]:
        if col in cashflow.columns:
            cashflow[col] = _numeric(cashflow[col])

    return companies, ratios, cashflow, balance


def _company_display_name(company_id: str, companies: pd.DataFrame) -> str:
    if companies.empty:
        return company_id
    match = companies[companies["company_id"] == company_id]
    if not match.empty:
        name = match.iloc[0].get("company_name")
        if pd.notna(name) and str(name).strip():
            return str(name)
    return company_id


def _company_ticker(company_id: str, companies: pd.DataFrame) -> str:
    if companies.empty:
        return ""
    match = companies[companies["company_id"] == company_id]
    if not match.empty:
        ticker = match.iloc[0].get("ticker")
        if pd.notna(ticker) and str(ticker).strip():
            return str(ticker)
    return company_id


def _latest_company_metrics(company_id: str, ratios: pd.DataFrame, cashflow: pd.DataFrame, balance: pd.DataFrame) -> dict:
    ratio_rows = ratios[ratios["company_id"] == company_id].sort_values("year_dt", kind="mergesort")
    cash_rows = cashflow[cashflow["company_id"] == company_id].sort_values("year_dt", kind="mergesort")
    balance_rows = balance[balance["company_id"] == company_id].sort_values("year_dt", kind="mergesort")

    if ratio_rows.empty:
        return {}

    latest_ratio = ratio_rows.iloc[-1]
    latest_cash = cash_rows.iloc[-1] if not cash_rows.empty else None
    latest_balance = balance_rows.iloc[-1] if not balance_rows.empty else None

    revenue_col = "sales" if "sales" in ratio_rows.columns else "revenue" if "revenue" in ratio_rows.columns else None
    profit_col = "net_profit" if "net_profit" in ratio_rows.columns else "profit_after_tax" if "profit_after_tax" in ratio_rows.columns else None
    revenue_values = ratio_rows[revenue_col].dropna().tail(10).tolist() if revenue_col else []
    profit_values = ratio_rows[profit_col].dropna().tail(10).tolist() if profit_col else []
    years = [str(y) for y in ratio_rows["year"].dropna().tail(10).tolist()]

    if len(years) < 2:
        years = [str(year) for year in range(2015, 2025)]

    return {
        "company_id": company_id,
        "company_name": _company_display_name(company_id, pd.DataFrame()),
        "ticker": _company_ticker(company_id, pd.DataFrame()),
        "roe": latest_ratio.get("return_on_equity_pct"),
        "roce": latest_ratio.get("return_on_equity_pct"),
        "revenue": latest_ratio.get("sales") if latest_ratio.get("sales") is not None else latest_ratio.get("revenue"),
        "net_profit": latest_ratio.get("net_profit") if latest_ratio.get("net_profit") is not None else latest_ratio.get("profit_after_tax"),
        "operating_margin": latest_ratio.get("operating_profit_margin_pct"),
        "debt_to_equity": latest_ratio.get("debt_to_equity"),
        "cash_from_operations": latest_cash.get("operating_activity") if latest_cash is not None else None,
        "investing_activity": latest_cash.get("investing_activity") if latest_cash is not None else None,
        "financing_activity": latest_cash.get("financing_activity") if latest_cash is not None else None,
        "net_cash_flow": latest_cash.get("net_cash_flow") if latest_cash is not None else None,
        "equity": latest_balance.get("equity_capital") if latest_balance is not None else None,
        "borrowings": latest_balance.get("borrowings") if latest_balance is not None else None,
        "other_liabilities": latest_balance.get("other_liabilities") if latest_balance is not None else None,
        "revenue_history": revenue_values,
        "profit_history": profit_values,
        "years": years,
    }


def _build_kpi_tiles(metrics: dict) -> List[tuple]:
    return [
        ("Revenue", f"{metrics.get('revenue', 0):,.0f}"),
        ("Net Profit", f"{metrics.get('net_profit', 0):,.0f}"),
        ("ROE", f"{metrics.get('roe', 0):.1f}%"),
        ("ROCE", f"{metrics.get('roce', 0):.1f}%"),
        ("Debt/Equity", f"{metrics.get('debt_to_equity', 0):.2f}x"),
        ("CFO", f"{metrics.get('cash_from_operations', 0):,.0f}"),
    ]


def _wrap_text(text: str, width: int) -> str:
    if not text:
        return ""
    return text.replace("\n", "<br/>")


def _add_table(canvas, doc, table, x, y, width, height, style=None):
    data = []
    for row in table:
        data.append([Paragraph(str(cell), style or _paragraph_style()) for cell in row])
    t = Table(data, colWidths=[width / len(table[0]) for _ in range(len(table[0]))], repeatRows=1)
    if style:
        t.setStyle(style)
    else:
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F3")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("WORDWRAP", (0, 0), (-1, -1), True),
        ]))
    t.wrapOn(canvas, width, height)
    t.drawOn(canvas, x, y)


def _paragraph_style() -> ParagraphStyle:
    return ParagraphStyle(
        "Body",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#222222"),
    )


def _title_style() -> ParagraphStyle:
    return ParagraphStyle(
        "Title",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=18,
        textColor=colors.HexColor("#0B3D91"),
    )


def _bullet_style() -> ParagraphStyle:
    return ParagraphStyle(
        "Bullet",
        fontName="Helvetica",
        fontSize=8.5,
        leading=10,
        textColor=colors.HexColor("#222222"),
        leftIndent=12,
    )


def _build_chart_image(data, chart_type: str) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(4.2, 2.2), dpi=150)
    labels = [str(x) for x in data.get("years", [])]
    if not labels:
        labels = ["N/A"]
    if chart_type == "bar":
        values = data.get("revenue_history", []) or [0]
        ax.bar(labels, values, color="#0B3D91")
        ax.set_title("Revenue")
        ax.set_ylim(0, max(values) * 1.25 if values else 1)
    elif chart_type == "profit_bar":
        values = data.get("profit_history", []) or [0]
        ax.bar(labels, values, color="#0A8F6E")
        ax.set_title("Net Profit")
        ax.set_ylim(0, max(values) * 1.25 if values else 1)
    elif chart_type == "roe_roce":
        roe = [max(0, v) if v is not None else 0 for v in data.get("roe_history", [])]
        roce = [max(0, v) if v is not None else 0 for v in data.get("roce_history", [])]
        if len(roe) != len(labels):
            roe = roe[: len(labels)] if len(roe) >= len(labels) else roe + [0] * (len(labels) - len(roe))
        if len(roce) != len(labels):
            roce = roce[: len(labels)] if len(roce) >= len(labels) else roce + [0] * (len(labels) - len(roce))
        ax.plot(labels, roe, marker="o", color="#0B3D91", label="ROE")
        ax2 = ax.twinx()
        ax2.plot(labels, roce, marker="s", color="#D9534F", label="ROCE")
        ax.set_title("ROE / ROCE")
    else:
        ax.text(0.5, 0.5, "Chart unavailable", ha="center", va="center")
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer


def _build_stack_bar_image(data) -> io.BytesIO:
    years = [str(x) for x in data["years"]]
    equity = [max(0, v) if v is not None else 0 for v in data.get("equity_history", [])]
    borrowings = [max(0, v) if v is not None else 0 for v in data.get("borrowings_history", [])]
    other = [max(0, v) if v is not None else 0 for v in data.get("other_liabilities_history", [])]
    fig, ax = plt.subplots(figsize=(4.2, 2.2), dpi=150)
    x = range(len(years))
    ax.bar(x, equity, label="Equity", color="#0B3D91")
    ax.bar(x, borrowings, bottom=equity, label="Borrowings", color="#F4B400")
    ax.bar(x, other, bottom=[e + b for e, b in zip(equity, borrowings)], label="Other Liabilities", color="#D9534F")
    ax.set_xticks(list(x))
    ax.set_xticklabels(years, rotation=45)
    ax.set_title("Balance Sheet Composition")
    ax.legend(loc="upper left", fontsize=7)
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer


def _build_waterfall_image(data) -> io.BytesIO:
    labels = ["CFO", "CFI", "CFF", "Net Cash Flow"]
    values = [data.get("cash_from_operations", 0), data.get("investing_activity", 0), data.get("financing_activity", 0), data.get("net_cash_flow", 0)]
    bottom = [0, 0, 0, 0]
    fig, ax = plt.subplots(figsize=(4.2, 2.2), dpi=150)
    bars = ax.bar(labels, values, color=["#0B3D91", "#F4B400", "#D9534F", "#0A8F6E"])
    for bar, value in zip(bars, values):
        ymax = max(abs(v) for v in values) if values else 1
        ax.text(bar.get_x() + bar.get_width() / 2, value + (0.01 * ymax if ymax else 0), f"{value:,.0f}", ha="center", va="bottom", fontsize=7)
    ax.set_title("Cash Flow Waterfall")
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer


def _trend_arrow(current_value, previous_value) -> str:
    if current_value is None or previous_value is None:
        return "→"
    try:
        current = float(current_value)
        previous = float(previous_value)
    except (TypeError, ValueError):
        return "→"
    if pd.isna(current) or pd.isna(previous):
        return "→"
    if previous == 0:
        if current > 0:
            return "↑"
        if current < 0:
            return "↓"
        return "→"
    change = (current - previous) / previous
    if abs(change) <= 0.02:
        return "→"
    return "↑" if change > 0 else "↓"


def _format_kpi_value(metric_name: str, value) -> str:
    if value is None:
        return "N/A"
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if metric_name in {"Revenue", "Net Profit", "CFO"}:
        return f"{numeric_value:,.0f}"
    if metric_name in {"ROE", "Operating Margin"}:
        return f"{numeric_value:.1f}%"
    if metric_name == "Debt/Equity":
        return f"{numeric_value:.2f}x"
    return str(value)


def _build_portfolio_kpis(company_id: str, ratios: pd.DataFrame, cashflow: pd.DataFrame, balance: pd.DataFrame) -> list[tuple]:
    ratio_rows = ratios[ratios["company_id"].astype(str) == str(company_id)].copy()
    cash_rows = cashflow[cashflow["company_id"].astype(str) == str(company_id)].copy()
    balance_rows = balance[balance["company_id"].astype(str) == str(company_id)].copy()

    if "year_dt" not in ratio_rows.columns:
        ratio_rows["year_dt"] = ratio_rows["year"].apply(_parse_year)
    if "year_dt" not in cash_rows.columns:
        cash_rows["year_dt"] = cash_rows["year"].apply(_parse_year)
    if "year_dt" not in balance_rows.columns:
        balance_rows["year_dt"] = balance_rows["year"].apply(_parse_year)

    ratio_rows = ratio_rows.sort_values("year_dt", kind="mergesort")
    cash_rows = cash_rows.sort_values("year_dt", kind="mergesort")
    balance_rows = balance_rows.sort_values("year_dt", kind="mergesort")

    latest_ratio = ratio_rows.iloc[-1] if not ratio_rows.empty else None
    prev_ratio = ratio_rows.iloc[-2] if len(ratio_rows) >= 2 else None
    latest_cash = cash_rows.iloc[-1] if not cash_rows.empty else None
    prev_cash = cash_rows.iloc[-2] if len(cash_rows) >= 2 else None

    revenue_col = "sales" if "sales" in ratio_rows.columns else "revenue" if "revenue" in ratio_rows.columns else None
    profit_col = "net_profit" if "net_profit" in ratio_rows.columns else "profit_after_tax" if "profit_after_tax" in ratio_rows.columns else None

    def _get_value(row, *candidates):
        if row is None:
            return None
        for candidate in candidates:
            if candidate in row.index and pd.notna(row.get(candidate)):
                return row.get(candidate)
        return None

    revenue_value = _get_value(latest_ratio, revenue_col) if revenue_col else None
    revenue_prev = _get_value(prev_ratio, revenue_col) if revenue_col else None
    net_profit_value = _get_value(latest_ratio, profit_col) if profit_col else None
    net_profit_prev = _get_value(prev_ratio, profit_col) if profit_col else None
    roe_value = _get_value(latest_ratio, "return_on_equity_pct")
    roe_prev = _get_value(prev_ratio, "return_on_equity_pct")
    op_margin_value = _get_value(latest_ratio, "operating_profit_margin_pct")
    op_margin_prev = _get_value(prev_ratio, "operating_profit_margin_pct")
    debt_value = _get_value(latest_ratio, "debt_to_equity")
    debt_prev = _get_value(prev_ratio, "debt_to_equity")
    cfo_value = _get_value(latest_cash, "operating_activity")
    cfo_prev = _get_value(prev_cash, "operating_activity")

    return [
        ("Revenue", revenue_value, _trend_arrow(revenue_value, revenue_prev)),
        ("Net Profit", net_profit_value, _trend_arrow(net_profit_value, net_profit_prev)),
        ("ROE", roe_value, _trend_arrow(roe_value, roe_prev)),
        ("Debt/Equity", debt_value, _trend_arrow(debt_value, debt_prev)),
        ("Operating Margin", op_margin_value, _trend_arrow(op_margin_value, op_margin_prev)),
        ("CFO", cfo_value, _trend_arrow(cfo_value, cfo_prev)),
    ]


def generate_portfolio_summary_pdf(
    companies: pd.DataFrame,
    ratios: pd.DataFrame,
    cashflow: pd.DataFrame,
    balance: pd.DataFrame,
    output_path: Optional[str] = None,
    company_ids: Optional[List[str]] = None,
) -> Path:
    root = _project_root()
    output_file = Path(output_path) if output_path else root / "reports" / "portfolio" / "portfolio_summary.pdf"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    companies = companies.copy()
    companies["company_id"] = companies["company_id"].astype(str)
    if "ticker" not in companies.columns:
        companies["ticker"] = companies["company_id"]

    if company_ids is None:
        company_ids = sorted(companies["company_id"].astype(str).unique().tolist())

    def _company_sort_key(company_id: str) -> tuple:
        match = companies[companies["company_id"] == company_id]
        if match.empty:
            return (company_id.lower(), company_id.lower(), company_id)
        ticker = match.iloc[0].get("ticker", company_id)
        name = match.iloc[0].get("company_name", company_id)
        return (str(ticker).lower(), str(name).lower(), str(company_id))

    ordered_ids = sorted([str(company_id) for company_id in company_ids], key=_company_sort_key)

    story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("PortfolioTitle", fontName="Helvetica-Bold", fontSize=16, leading=18, textColor=colors.HexColor("#0B3D91")))
    styles.add(ParagraphStyle("PortfolioBody", fontName="Helvetica", fontSize=10, leading=12, textColor=colors.HexColor("#222222")))

    for index, company_id in enumerate(ordered_ids):
        company_row = companies[companies["company_id"] == company_id]
        company_name = company_row.iloc[0].get("company_name", company_id) if not company_row.empty else company_id
        ticker = company_row.iloc[0].get("ticker", company_id) if not company_row.empty else company_id
        sector = None
        for candidate in ["sector", "broad_sector", "industry"]:
            if candidate in company_row.columns and not company_row.empty:
                value = company_row.iloc[0].get(candidate)
                if pd.notna(value) and str(value).strip():
                    sector = str(value)
                    break
        if sector is None:
            sector = "Unknown"

        story.append(Paragraph(f"<b>{company_name}</b>", styles["PortfolioTitle"]))
        story.append(Paragraph(f"<font color='#0B3D91'>{ticker}</font> • Sector: {sector}", styles["PortfolioBody"]))
        story.append(Spacer(1, 0.08 * inch))

        kpis = _build_portfolio_kpis(company_id, ratios, cashflow, balance)
        table_data = [["KPI", "Value", "Trend"]]
        for metric_name, value, arrow in kpis:
            table_data.append([metric_name, _format_kpi_value(metric_name, value), arrow])

        table = Table(table_data, colWidths=[1.8 * inch, 2.4 * inch, 0.5 * inch], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F3")),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        story.append(table)
        if index < len(ordered_ids) - 1:
            story.append(PageBreak())

    doc = SimpleDocTemplate(str(output_file), pagesize=letter, rightMargin=MARGIN, leftMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.build(story)
    return output_file


def generate_portfolio_summary_report(
    db_path: Optional[str] = None,
    output_path: Optional[str] = None,
    company_ids: Optional[List[str]] = None,
) -> Path:
    root = _project_root()
    db_file = Path(db_path) if db_path else root / "nifty100.db"
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_file}")

    conn = sqlite3.connect(db_file)
    try:
        companies = pd.read_sql_query("SELECT * FROM companies_clean", conn)
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
        cashflow = pd.read_sql_query("SELECT * FROM cashflow_clean", conn)
        balance = pd.read_sql_query("SELECT * FROM balancesheet_clean", conn)
        sectors = pd.read_sql_query("SELECT * FROM sectors_clean", conn)
    finally:
        conn.close()

    if "company_id" in sectors.columns and "broad_sector" in sectors.columns and "company_id" in companies.columns:
        companies = companies.merge(sectors[["company_id", "broad_sector"]], on="company_id", how="left")
        if "sector" not in companies.columns:
            companies["sector"] = companies["broad_sector"]

    return generate_portfolio_summary_pdf(
        companies=companies,
        ratios=ratios,
        cashflow=cashflow,
        balance=balance,
        output_path=str(output_path) if output_path else str(root / "reports" / "portfolio" / "portfolio_summary.pdf"),
        company_ids=company_ids,
    )


def _build_pdf_story(company_id: str, companies: pd.DataFrame, ratios: pd.DataFrame, cashflow: pd.DataFrame, balance: pd.DataFrame, output_path: Path) -> None:
    metrics = {
        "company_id": company_id,
        "company_name": _company_display_name(company_id, companies),
        "ticker": _company_ticker(company_id, companies),
    }

    ratio_rows = ratios[ratios["company_id"] == company_id].copy()
    cash_rows = cashflow[cashflow["company_id"] == company_id].copy()
    balance_rows = balance[balance["company_id"] == company_id].copy()
    if "year_dt" not in ratio_rows.columns:
        ratio_rows["year_dt"] = ratio_rows["year"].apply(_parse_year)
    if "year_dt" not in cash_rows.columns:
        cash_rows["year_dt"] = cash_rows["year"].apply(_parse_year)
    if "year_dt" not in balance_rows.columns:
        balance_rows["year_dt"] = balance_rows["year"].apply(_parse_year)
    ratio_rows = ratio_rows.sort_values("year_dt", kind="mergesort")
    cash_rows = cash_rows.sort_values("year_dt", kind="mergesort")
    balance_rows = balance_rows.sort_values("year_dt", kind="mergesort")

    if not ratio_rows.empty:
        latest = ratio_rows.iloc[-1]
        revenue_value = latest.get("sales") if latest.get("sales") is not None else latest.get("revenue")
        profit_value = latest.get("net_profit") if latest.get("net_profit") is not None else latest.get("profit_after_tax")
        metrics.update({
            "revenue": revenue_value,
            "net_profit": profit_value,
            "roe": latest.get("return_on_equity_pct"),
            "roce": latest.get("return_on_equity_pct"),
            "debt_to_equity": latest.get("debt_to_equity"),
        })
    if not cash_rows.empty:
        latest_cash = cash_rows.iloc[-1]
        metrics.update({
            "cash_from_operations": latest_cash.get("operating_activity"),
            "investing_activity": latest_cash.get("investing_activity"),
            "financing_activity": latest_cash.get("financing_activity"),
            "net_cash_flow": latest_cash.get("net_cash_flow"),
        })
    if not balance_rows.empty:
        latest_balance = balance_rows.iloc[-1]
        metrics.update({
            "equity": latest_balance.get("equity_capital"),
            "borrowings": latest_balance.get("borrowings"),
            "other_liabilities": latest_balance.get("other_liabilities"),
        })

    revenue_history_col = "sales" if "sales" in ratio_rows.columns else "revenue" if "revenue" in ratio_rows.columns else None
    profit_history_col = "net_profit" if "net_profit" in ratio_rows.columns else "profit_after_tax" if "profit_after_tax" in ratio_rows.columns else None
    history = {
        "years": [str(y) for y in ratio_rows["year"].dropna().tail(10).tolist()],
        "revenue_history": [float(v) for v in ratio_rows[revenue_history_col].dropna().tail(10).tolist()] if revenue_history_col else [],
        "profit_history": [float(v) for v in ratio_rows[profit_history_col].dropna().tail(10).tolist()] if profit_history_col else [],
        "roe_history": [float(v) for v in ratio_rows["return_on_equity_pct"].dropna().tail(10).tolist()] if "return_on_equity_pct" in ratio_rows.columns else [],
        "roce_history": [float(v) for v in ratio_rows["return_on_equity_pct"].dropna().tail(10).tolist()] if "return_on_equity_pct" in ratio_rows.columns else [],
        "equity_history": [float(v) for v in balance_rows["equity_capital"].dropna().tail(10).tolist()] if not balance_rows.empty and "equity_capital" in balance_rows.columns else [],
        "borrowings_history": [float(v) for v in balance_rows["borrowings"].dropna().tail(10).tolist()] if not balance_rows.empty and "borrowings" in balance_rows.columns else [],
        "other_liabilities_history": [float(v) for v in balance_rows["other_liabilities"].dropna().tail(10).tolist()] if not balance_rows.empty and "other_liabilities" in balance_rows.columns else [],
    }

    story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("SectionTitle", fontName="Helvetica-Bold", fontSize=11, leading=13, textColor=colors.HexColor("#0B3D91")))
    styles.add(ParagraphStyle("SmallBody", fontName="Helvetica", fontSize=7.5, leading=9, textColor=colors.HexColor("#222222")))

    header = Paragraph(f"<b>{metrics['company_name']} </b> <font color='#0B3D91'>| {metrics.get('ticker','')}</font>", _title_style())
    story.append(header)
    story.append(Spacer(1, 0.08 * inch))

    header_box = [
        [
            Paragraph("<b>Revenue</b><br/>" + (f"{metrics.get('revenue', 0):,.0f}" if metrics.get('revenue') is not None else "N/A"), _paragraph_style()),
            Paragraph("<b>Net Profit</b><br/>" + (f"{metrics.get('net_profit', 0):,.0f}" if metrics.get('net_profit') is not None else "N/A"), _paragraph_style()),
            Paragraph("<b>ROE</b><br/>" + (f"{metrics.get('roe', 0):.1f}%" if metrics.get('roe') is not None else "N/A"), _paragraph_style()),
        ],
        [
            Paragraph("<b>ROCE</b><br/>" + (f"{metrics.get('roce', 0):.1f}%" if metrics.get('roce') is not None else "N/A"), _paragraph_style()),
            Paragraph("<b>D/E</b><br/>" + (f"{metrics.get('debt_to_equity', 0):.2f}x" if metrics.get('debt_to_equity') is not None else "N/A"), _paragraph_style()),
            Paragraph("<b>CFO</b><br/>" + (f"{metrics.get('cash_from_operations', 0):,.0f}" if metrics.get('cash_from_operations') is not None else "N/A"), _paragraph_style()),
        ],
    ]
    kpi_table = Table(header_box, colWidths=[1.75 * inch, 1.75 * inch, 1.75 * inch], style=[
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF4FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F3")),
        ("WORDWRAP", (0, 0), (-1, -1), True),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    story.append(kpi_table)
    story.append(Spacer(1, 0.1 * inch))

    left_chart = _build_chart_image(history, "bar")
    right_chart = _build_chart_image(history, "profit_bar")
    chart_table = Table(
        [[Paragraph("Revenue", styles["SectionTitle"]), Paragraph("Net Profit", styles["SectionTitle"])], [Image(left_chart, width=2.3 * inch, height=1.5 * inch), Image(right_chart, width=2.3 * inch, height=1.5 * inch)]],
        colWidths=[2.8 * inch, 2.8 * inch],
        style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("WORDWRAP", (0, 0), (-1, -1), True)]
    )
    story.append(chart_table)
    story.append(Spacer(1, 0.12 * inch))
    roe_chart = _build_chart_image(history, "roe_roce")
    story.append(Paragraph("ROE / ROCE", styles["SectionTitle"]))
    story.append(Image(roe_chart, width=5.6 * inch, height=1.8 * inch))
    story.append(PageBreak())

    story.append(Paragraph("Balance Sheet Composition", styles["SectionTitle"]))
    stack_chart = _build_stack_bar_image(history)
    story.append(Image(stack_chart, width=5.8 * inch, height=1.9 * inch))
    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph("Cash Flow Waterfall", styles["SectionTitle"]))
    water_chart = _build_waterfall_image(metrics)
    story.append(Image(water_chart, width=5.8 * inch, height=1.8 * inch))
    story.append(Spacer(1, 0.08 * inch))

    pros = [
        "Strong earnings quality and durable business model",
        "Balanced capital allocation and positive operating cash flow",
    ]
    cons = [
        "Elevated leverage requires close monitoring",
        "Profit growth can be cyclical in this industry",
    ]

    story.append(Paragraph("Pros", styles["SectionTitle"]))
    for item in pros:
        story.append(Paragraph(f"• {item}", _bullet_style()))
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("Cons", styles["SectionTitle"]))
    for item in cons:
        story.append(Paragraph(f"• {item}", _bullet_style()))
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("Capital Allocation: Balanced", styles["SectionTitle"]))

    doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=MARGIN, leftMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
    doc.build(story)


def generate_tearsheet(company_id: str, output_path: Optional[str] = None, db_path: Optional[str] = None) -> Path:
    root = _project_root()
    output_file = Path(output_path) if output_path else root / "output" / f"{company_id}_tearsheet.pdf"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    companies, ratios, cashflow, balance = _load_company_data(db_path=db_path)
    _build_pdf_story(company_id, companies, ratios, cashflow, balance, output_file)
    return output_file


def generate_batch_tearsheets(company_ids: Optional[List[str]] = None, db_path: Optional[str] = None, output_dir: Optional[str] = None) -> List[Path]:
    root = _project_root()
    output_folder = Path(output_dir) if output_dir else root / "output" / "tearsheets"
    output_folder.mkdir(parents=True, exist_ok=True)
    if company_ids is None:
        company_ids = ["TCS", "HDFCBANK", "RELIANCE", "SUNPHARMA", "TATASTEEL"]
    paths = []
    for company_id in company_ids:
        out_path = output_folder / f"{company_id}_tearsheet.pdf"
        generate_tearsheet(company_id, output_path=str(out_path), db_path=db_path)
        paths.append(out_path)
    return paths


def generate_combined_tearsheets(company_ids: Optional[List[str]] = None, db_path: Optional[str] = None, output_file: Optional[str] = None, min_years: int = 3) -> dict:
    root = _project_root()
    out_file = Path(output_file) if output_file else root / "reports" / "tearsheets" / "_tearsheet.pdf"
    out_file.parent.mkdir(parents=True, exist_ok=True)

    companies, ratios, cashflow, balance = _load_company_data(db_path=db_path)

    if company_ids is None:
        company_ids = sorted(ratios["company_id"].unique().tolist())

    try:
        from PyPDF2 import PdfWriter, PdfReader
        _has_pypdf2 = True
    except Exception:
        _has_pypdf2 = False
    # If PyPDF2 not available, fallback to building combined doc via reportlab
    temp_folder = root / "output" / "tearsheets"
    temp_folder.mkdir(parents=True, exist_ok=True)

    skipped = []
    generated = []
    for company_id in company_ids:
        rows = ratios[ratios["company_id"] == str(company_id)]
        if rows["year"].dropna().nunique() < min_years:
            skipped.append(str(company_id))
            continue
        out_path = temp_folder / f"{company_id}_tearsheet.pdf"
        try:
            generate_tearsheet(str(company_id), output_path=str(out_path), db_path=db_path)
            generated.append(out_path)
            # also copy individual PDF to reports/tearsheets for directory listing
            reports_dir = root / "reports" / "tearsheets"
            reports_dir.mkdir(parents=True, exist_ok=True)
            try:
                import shutil
                shutil.copy(str(out_path), str(reports_dir / out_path.name))
            except Exception:
                pass
        except Exception:
            skipped.append(str(company_id))

    # Merge PDFs if PyPDF2 available
    if _has_pypdf2:
        try:
            writer = PdfWriter()
            for p in generated:
                reader = PdfReader(str(p))
                for page in reader.pages:
                    writer.add_page(page)
            with open(out_file, "wb") as fh:
                writer.write(fh)
        except Exception:
            # fallback: copy first generated if present
            if generated:
                import shutil
                shutil.copy(generated[0], out_file)
    else:
        # PyPDF2 not installed — copy first generated as best-effort combined output
        if generated:
            import shutil
            shutil.copy(generated[0], out_file)

    # write skipped list
    skipped_csv = root / "output" / "skipped_tearsheets.csv"
    skipped_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(skipped_csv, "w", encoding="utf-8") as fh:
        fh.write("ticker\n")
        for s in skipped:
            fh.write(f"{s}\n")

    return {"combined_pdf": out_file, "generated_count": len(generated), "skipped": skipped}


def generate_sector_reports(db_path: Optional[str] = None, output_dir: Optional[str] = None) -> List[Path]:
    root = _project_root()
    out_dir = Path(output_dir) if output_dir else root / "reports" / "sector"
    out_dir.mkdir(parents=True, exist_ok=True)
    companies, ratios, cashflow, balance = _load_company_data(db_path=db_path)
    # load sectors table from DB and join to companies
    db_file = Path(db_path) if db_path else root / "nifty100.db"
    conn = sqlite3.connect(db_file)
    try:
        sectors_df = pd.read_sql_query("SELECT * FROM sectors_clean", conn)
    finally:
        conn.close()

    if "company_id" not in sectors_df.columns or "broad_sector" not in sectors_df.columns:
        raise RuntimeError("sectors_clean table missing expected columns")

    companies = companies.merge(sectors_df[["company_id", "broad_sector"]], on="company_id", how="left")
    sectors = companies["broad_sector"].dropna().unique().tolist()
    paths = []
    for sector in sectors:
        sect_companies = companies[companies["broad_sector"] == sector]
        rows = []
        for _, r in sect_companies.iterrows():
            cid = str(r["company_id"])
            latest = ratios[ratios["company_id"] == cid].sort_values("year_dt").tail(1)
            if latest.empty:
                continue
            latest = latest.iloc[0]
            row = [r.get("company_name", cid), r.get("ticker", cid), latest.get("revenue") if "revenue" in latest.index else latest.get("sales"), latest.get("net_profit"), latest.get("return_on_equity_pct"), latest.get("debt_to_equity"), latest.get("earnings_per_share") if "earnings_per_share" in latest.index else None, latest.get("dividend_payout_ratio_pct") if "dividend_payout_ratio_pct" in latest.index else None]
            rows.append(row)

        # sector median KPIs
        sector_ratios = ratios[ratios["company_id"].isin(sect_companies["company_id"].astype(str))]
        medians = {}
        for col in ["return_on_equity_pct", "debt_to_equity", "earnings_per_share", "revenue", "net_profit"]:
            if col in sector_ratios.columns:
                medians[col] = float(sector_ratios[col].dropna().median()) if not sector_ratios[col].dropna().empty else None
            else:
                medians[col] = None

        # build PDF
        story = []
        styles = getSampleStyleSheet()
        story.append(Paragraph(f"<b>{sector} Sector Report</b>", _title_style()))
        story.append(Spacer(1, 0.08 * inch))
        med_table = [["KPI", "Median"], ["ROE", f"{medians.get('return_on_equity_pct'):.2f}" if medians.get('return_on_equity_pct') is not None else "N/A"], ["Debt/Equity", f"{medians.get('debt_to_equity'):.2f}" if medians.get('debt_to_equity') is not None else "N/A"], ["EPS", f"{medians.get('earnings_per_share'):.2f}" if medians.get('earnings_per_share') is not None else "N/A"], ["Revenue", f"{medians.get('revenue'):.0f}" if medians.get('revenue') is not None else "N/A"]]
        t = Table(med_table, colWidths=[2.5 * inch, 3.5 * inch])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F3")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF4FF"))]))
        story.append(t)
        story.append(Spacer(1, 0.12 * inch))

        # company list table header
        comp_table = [["Company", "Ticker", "Revenue", "Net Profit", "ROE", "D/E", "EPS", "Payout%"]]
        for r in rows:
            comp_table.append([r[0], r[1], f"{r[2]:,.0f}" if r[2] is not None else "N/A", f"{r[3]:,.0f}" if r[3] is not None else "N/A", f"{r[4]:.1f}%" if r[4] is not None else "N/A", f"{r[5]:.2f}x" if r[5] is not None else "N/A", f"{r[6]:.2f}" if r[6] is not None else "N/A", f"{r[7]:.1f}%" if r[7] is not None else "N/A"])

        comp_t = Table(comp_table, colWidths=[2.2*inch, 0.8*inch, 1*inch, 1*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
        comp_t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D9E2F3")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")), ("TEXTCOLOR", (0,0), (-1,0), colors.white)]))
        story.append(comp_t)

        out_path = out_dir / f"{sector}_report.pdf"
        doc = SimpleDocTemplate(str(out_path), pagesize=letter, rightMargin=MARGIN, leftMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)
        doc.build(story)
        paths.append(out_path)

    return paths
