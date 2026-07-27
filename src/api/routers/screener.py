import sqlite3

from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
def screener(

    min_roe: float | None = Query(None),

    max_de: float | None = Query(None),

    min_fcf: float | None = Query(None),

    sector: str | None = Query(None),

    min_rev_cagr_5yr: float | None = Query(None),

    min_pat_cagr_5yr: float | None = Query(None),

    max_pe: float | None = Query(None)

):

    # ---------------------------------------------------------
    # Parameter Validation
    # ---------------------------------------------------------

    if min_roe is not None and min_roe < -100:
        raise HTTPException(
            status_code=400,
            detail="Invalid min_roe"
        )

    if max_de is not None and max_de < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid max_de"
        )

    if max_pe is not None and max_pe < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid max_pe"
        )

    conn = get_db_connection()

    query = """
    SELECT

        c.company_id,

        c.company_name,

        s.broad_sector,

        fr.return_on_equity_pct,

        fr.debt_to_equity,

        fr.free_cash_flow_cr,

        fr.revenue_cagr_5yr,

        fr.pat_cagr_5yr,

        mc.pe_ratio,

        mc.pb_ratio,

        mc.market_cap_crore

    FROM companies_clean c

    LEFT JOIN sectors_clean s

        ON c.company_id = s.company_id

    LEFT JOIN financial_ratios fr

        ON c.company_id = fr.company_id

    LEFT JOIN market_cap_clean mc

        ON c.company_id = mc.company_id

    WHERE

        fr.year = (

            SELECT MAX(year)

            FROM financial_ratios f2

            WHERE f2.company_id = c.company_id

        )

    AND

        mc.year = (

            SELECT MAX(year)

            FROM market_cap_clean m2

            WHERE m2.company_id = c.company_id

        )
    """

    params = []

    if min_roe is not None:
        query += " AND fr.return_on_equity_pct >= ?"
        params.append(min_roe)

    if max_de is not None:
        query += " AND fr.debt_to_equity <= ?"
        params.append(max_de)

    if min_fcf is not None:
        query += " AND fr.free_cash_flow_cr >= ?"
        params.append(min_fcf)

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if min_rev_cagr_5yr is not None:
        query += " AND fr.revenue_cagr_5yr >= ?"
        params.append(min_rev_cagr_5yr)

    if min_pat_cagr_5yr is not None:
        query += " AND fr.pat_cagr_5yr >= ?"
        params.append(min_pat_cagr_5yr)

    if max_pe is not None:
        query += " AND mc.pe_ratio <= ?"
        params.append(max_pe)

    query += """

    ORDER BY

        fr.return_on_equity_pct DESC,

        fr.free_cash_flow_cr DESC
    """

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]