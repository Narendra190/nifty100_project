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
