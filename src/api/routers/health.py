import sqlite3
import time

from fastapi import APIRouter

router = APIRouter()

APP_START_TIME = time.time()

DATABASE_PATH = "nifty100.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
def health():

    conn = get_db_connection()

    cursor = conn.cursor()

    tables = [
        "companies_clean",
        "balancesheet_clean",
        "cashflow_clean",
        "profitandloss_clean",
        "stock_prices",
        "financial_ratios",
        "sectors_clean",
        "peer_groups_clean",
        "documents_clean",
        "analysis_clean"
    ]

    row_counts = {}

    for table in tables:

        try:

            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            row_counts[table] = cursor.fetchone()[0]

        except Exception:

            row_counts[table] = "Table Not Found"

    conn.close()

    uptime = round(
        time.time() - APP_START_TIME,
        2
    )

    return {

        "status": "ok",

        "db_row_counts": row_counts,

        "uptime_seconds": uptime,

        "version": "1.0.0"

    }