import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/{ticker}")
def company_documents(ticker: str):

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT

            Year,

            Annual_Report

        FROM documents_clean

        WHERE company_id = ?

        ORDER BY Year DESC
        """,
        (ticker.upper(),)
    ).fetchall()

    conn.close()

    if len(rows) == 0:

        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    output = []

    for row in rows:

        url = row["Annual_Report"]

        output.append(
            {
                "year": row["Year"],
                "annual_report": url,
                "is_url_valid":
                    isinstance(url, str)
                    and (
                        url.startswith("http://")
                        or url.startswith("https://")
                    )
            }
        )

    return output