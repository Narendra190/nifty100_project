import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================================
# GET /api/v1/peers/{group_name}
# ==========================================================

@router.get("/{group_name}")
def get_peer_group(group_name: str):

    conn = get_db_connection()

    exists = conn.execute(
        """
        SELECT 1
        FROM peer_groups_clean
        WHERE peer_group_name = ?
        LIMIT 1
        """,
        (group_name,)
    ).fetchone()

    if exists is None:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Peer group not found"
        )

    query = """
    SELECT

        pg.peer_group_name,

        pg.company_id,

        c.company_name,

        pg.is_benchmark,

        fr.return_on_equity_pct,

        fr.debt_to_equity,

        fr.net_profit_margin_pct,

        fr.operating_profit_margin_pct,

        fr.asset_turnover,

        fr.interest_coverage,

        fr.free_cash_flow_cr,

        fr.revenue_cagr_5yr,

        fr.pat_cagr_5yr,

        fr.earnings_per_share

    FROM peer_groups_clean pg

    JOIN companies_clean c

        ON pg.company_id = c.company_id

    LEFT JOIN financial_ratios fr

        ON pg.company_id = fr.company_id

    WHERE

        pg.peer_group_name = ?

    AND

        fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = pg.company_id
        )

    ORDER BY

        fr.return_on_equity_pct DESC
    """

    rows = conn.execute(
        query,
        (group_name,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ==========================================================
# GET /api/v1/companies/{ticker}/peers/compare
# ==========================================================

@router.get("/compare/{ticker}")
def compare_with_peers(ticker: str):

    conn = get_db_connection()

    peer = conn.execute(
        """
        SELECT peer_group_name
        FROM peer_groups_clean
        WHERE company_id = ?
        """,
        (ticker.upper(),)
    ).fetchone()

    if peer is None:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    peer_group = peer["peer_group_name"]

    benchmark = conn.execute(
        """
        SELECT company_id
        FROM peer_groups_clean
        WHERE
            peer_group_name = ?
            AND is_benchmark = 1
        """,
        (peer_group,)
    ).fetchone()["company_id"]

    metrics = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "asset_turnover",
        "interest_coverage",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr"
    ]

    metric_sql = ", ".join(metrics)

    company = conn.execute(
        f"""
        SELECT {metric_sql}
        FROM financial_ratios
        WHERE
            company_id = ?
        ORDER BY year DESC
        LIMIT 1
        """,
        (ticker.upper(),)
    ).fetchone()

    benchmark_row = conn.execute(
        f"""
        SELECT {metric_sql}
        FROM financial_ratios
        WHERE
            company_id = ?
        ORDER BY year DESC
        LIMIT 1
        """,
        (benchmark,)
    ).fetchone()

    peer_avg = conn.execute(
        f"""
        SELECT

            AVG(return_on_equity_pct) AS return_on_equity_pct,
            AVG(net_profit_margin_pct) AS net_profit_margin_pct,
            AVG(operating_profit_margin_pct) AS operating_profit_margin_pct,
            AVG(asset_turnover) AS asset_turnover,
            AVG(interest_coverage) AS interest_coverage,
            AVG(free_cash_flow_cr) AS free_cash_flow_cr,
            AVG(revenue_cagr_5yr) AS revenue_cagr_5yr,
            AVG(pat_cagr_5yr) AS pat_cagr_5yr

        FROM financial_ratios

        WHERE company_id IN (

            SELECT company_id

            FROM peer_groups_clean

            WHERE peer_group_name = ?

        )

        AND year = (

            SELECT MAX(year)

            FROM financial_ratios f2

            WHERE f2.company_id = financial_ratios.company_id

        )
        """,
        (peer_group,)
    ).fetchone()

    conn.close()

    return {
        "peer_group": peer_group,
        "benchmark_company": benchmark,
        "metrics": metrics,
        "company": dict(company),
        "peer_average": dict(peer_avg),
        "benchmark": dict(benchmark_row)
    }