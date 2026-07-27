import sqlite3
from fastapi import APIRouter, HTTPException

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================================
# GET /api/v1/sectors
# ==========================================================

@router.get("/")
def get_sectors():

    conn = get_db_connection()

    query = """
    SELECT

        s.broad_sector,

        COUNT(DISTINCT s.company_id) AS company_count,

        ROUND(AVG(fr.return_on_equity_pct),2) AS median_roe,

        ROUND(AVG(mc.pe_ratio),2) AS median_pe,

        ROUND(AVG(fr.debt_to_equity),2) AS median_de

    FROM sectors_clean s

    LEFT JOIN financial_ratios fr

        ON s.company_id = fr.company_id

    LEFT JOIN market_cap_clean mc

        ON s.company_id = mc.company_id

    WHERE

        fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = s.company_id
        )

    AND

        mc.year = (
            SELECT MAX(year)
            FROM market_cap_clean m2
            WHERE m2.company_id = s.company_id
        )

    GROUP BY s.broad_sector

    ORDER BY s.broad_sector
    """

    rows = conn.execute(query).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ==========================================================
# GET /api/v1/sectors/{sector}/companies
# ==========================================================

@router.get("/{sector}/companies")
def get_sector_companies(sector: str):

    conn = get_db_connection()

    exists = conn.execute(
        """
        SELECT 1
        FROM sectors_clean
        WHERE broad_sector = ?
        LIMIT 1
        """,
        (sector,)
    ).fetchone()

    if exists is None:

        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Sector not found"
        )

    query = """
    SELECT

        c.company_id,

        c.company_name,

        fr.return_on_equity_pct,

        fr.debt_to_equity,

        fr.free_cash_flow_cr,

        fr.revenue_cagr_5yr,

        fr.pat_cagr_5yr,

        mc.pe_ratio,

        mc.pb_ratio,

        mc.market_cap_crore

    FROM companies_clean c

    JOIN sectors_clean s

        ON c.company_id = s.company_id

    LEFT JOIN financial_ratios fr

        ON c.company_id = fr.company_id

    LEFT JOIN market_cap_clean mc

        ON c.company_id = mc.company_id

    WHERE

        s.broad_sector = ?

    AND

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

    ORDER BY c.company_name
    """

    rows = conn.execute(
        query,
        (sector,)
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]