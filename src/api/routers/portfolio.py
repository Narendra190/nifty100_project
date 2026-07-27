import sqlite3

from fastapi import APIRouter

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/stats")
def portfolio_stats():

    conn = get_db_connection()

    query = """
    SELECT

        return_on_equity_pct,

        debt_to_equity,

        revenue_cagr_5yr,

        pat_cagr_5yr,

        net_profit_margin_pct,

        operating_profit_margin_pct,

        free_cash_flow_cr,

        asset_turnover,

        interest_coverage,

        earnings_per_share

    FROM financial_ratios

    WHERE year = (

        SELECT MAX(year)

        FROM financial_ratios f2

        WHERE f2.company_id = financial_ratios.company_id

    )
    """

    rows = conn.execute(query).fetchall()

    conn.close()

    return [dict(r) for r in rows]