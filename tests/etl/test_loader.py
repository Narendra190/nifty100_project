import sqlite3
import pandas as pd
import tempfile
import os

from src.loader import load_excel_to_table


def test_load_excel_returns_row_count():

    df = pd.DataFrame({
        "A": [1, 2],
        "B": [3, 4]
    })

    temp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    temp.close()

    try:
        df.to_excel(temp.name, index=False)

        conn = sqlite3.connect(":memory:")

        rows = load_excel_to_table(
            temp.name,
            "sample",
            conn
        )

        assert rows == 2

        conn.close()

    finally:
        os.remove(temp.name)


def test_table_created():

    df = pd.DataFrame({
        "A": [1]
    })

    temp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    temp.close()

    try:

        df.to_excel(temp.name, index=False)

        conn = sqlite3.connect(":memory:")

        load_excel_to_table(
            temp.name,
            "sample",
            conn
        )

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sample")

        assert cursor.fetchone()[0] == 1

        conn.close()

    finally:
        os.remove(temp.name)