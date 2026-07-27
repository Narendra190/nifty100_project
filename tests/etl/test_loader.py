import os
import sqlite3
import sys
import pandas as pd

sys.path.append(os.path.abspath("src"))

from loader import load_excel_to_table


def test_load_excel_to_table(tmp_path):

    excel = tmp_path / "sample.xlsx"
    db = tmp_path / "test.db"

    df = pd.DataFrame({
        "A":[1,2],
        "B":[3,4]
    })

    df.to_excel(excel,index=False)

    conn = sqlite3.connect(db)

    rows = load_excel_to_table(excel,"sample",conn)

    assert rows == 2

    loaded = pd.read_sql("SELECT * FROM sample",conn)

    assert len(loaded) == 2

    conn.close()


def test_table_columns(tmp_path):

    excel = tmp_path/"sample.xlsx"
    db = tmp_path/"test.db"

    pd.DataFrame({
        "Name":["A"],
        "Age":[20]
    }).to_excel(excel,index=False)

    conn = sqlite3.connect(db)

    load_excel_to_table(excel,"people",conn)

    loaded = pd.read_sql("SELECT * FROM people",conn)

    assert list(loaded.columns)==["Name","Age"]

    conn.close()