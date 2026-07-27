import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/{ticker}")
def market_cap_history(ticker: str):

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT

            year,

            market_cap_crore,

            pe_ratio,

            pb_ratio,

            ev_ebitda,

            dividend_yield_pct

        FROM market_cap_clean

        WHERE company_id = ?

        ORDER BY year
        """,
        (ticker.upper(),)
    ).fetchall()

    conn.close()

    if len(rows) == 0:

        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return [dict(r) for r in rows]