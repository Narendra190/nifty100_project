import os
import sqlite3

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# GET /api/v1/companies
# ============================================================

@router.get("/")
def get_companies(
    sector: str | None = Query(None),
    market_cap_category: str | None = Query(None),
    search: str | None = Query(None)
):

    conn = get_db_connection()

    query = """
    SELECT
        c.company_id,
        TRIM(c.company_name) AS company_name,
        s.broad_sector,
        s.sub_sector,
        c.roe_percentage AS roe_pct,
        c.roce_percentage AS roce_pct,
        s.market_cap_category

    FROM companies_clean c

    LEFT JOIN sectors_clean s
        ON c.company_id = s.company_id

    WHERE 1=1
    """

    params = []

    if sector:
        query += " AND s.broad_sector = ?"
        params.append(sector)

    if market_cap_category:
        query += " AND s.market_cap_category = ?"
        params.append(market_cap_category)

    if search:
        query += """
        AND (
            c.company_name LIKE ?
            OR c.company_id LIKE ?
        )
        """

        params.extend([
            f"%{search}%",
            f"%{search}%"
        ])

    query += """
    ORDER BY c.company_name
    """

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# GET /api/v1/companies/{ticker}
# ============================================================

@router.get("/{ticker}")
def get_company_profile(ticker: str):

    conn = get_db_connection()

    query = """
    SELECT

        c.*,

        s.broad_sector,
        s.sub_sector,
        s.market_cap_category,
        s.index_weight_pct,

        fr.*

    FROM companies_clean c

    LEFT JOIN sectors_clean s
        ON c.company_id = s.company_id

    LEFT JOIN financial_ratios fr
        ON c.company_id = fr.company_id

    WHERE
        c.company_id = ?

    AND fr.year = (

        SELECT MAX(year)

        FROM financial_ratios

        WHERE company_id = c.company_id

    )
    """

    row = conn.execute(
        query,
        (ticker.upper(),)
    ).fetchone()

    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return dict(row)

# ============================================================
# GET /api/v1/companies/{ticker}/pl
# ============================================================

@router.get("/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: str | None = Query(None),
    to_year: str | None = Query(None)
):

    conn = get_db_connection()

    query = """
    SELECT *
    FROM profitandloss_clean
    WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# GET /api/v1/companies/{ticker}/bs
# ============================================================

@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = Query(None),
    to_year: str | None = Query(None)
):

    conn = get_db_connection()

    query = """
    SELECT *
    FROM balancesheet_clean
    WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# GET /api/v1/companies/{ticker}/cashflow
# ============================================================

@router.get("/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = Query(None),
    to_year: str | None = Query(None)
):

    conn = get_db_connection()

    query = """
    SELECT *
    FROM cashflow_clean
    WHERE company_id = ?
    """

    params = [ticker.upper()]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return [dict(row) for row in rows]

# ============================================================
# GET /api/v1/companies/{ticker}/ratios
# ============================================================

@router.get("/{ticker}/ratios")
def get_financial_ratios(
    ticker: str,
    year: str | None = Query(None)
):

    conn = get_db_connection()

    query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    """

    params = [ticker.upper()]

    if year:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY year DESC"

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    if len(rows) == 0:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return [dict(row) for row in rows]


# ============================================================
# GET /api/v1/companies/{ticker}/tearsheet
# ============================================================

@router.get("/{ticker}/tearsheet")
def download_tearsheet(ticker: str):

    filename = f"{ticker.upper()}_tearsheet.pdf"

    pdf_path = os.path.join(
        "reports",
        "tearsheets",
        filename
    )

    if not os.path.exists(pdf_path):

        raise HTTPException(
            status_code=404,
            detail="Tearsheet not found"
        )

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename
    )