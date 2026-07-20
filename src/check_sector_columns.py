import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

tables = [
    "sectors_clean",
    "companies_clean"
]

for table in tables:
    try:
        print(f"\n===== {table} =====")
        df = pd.read_sql(f"SELECT * FROM {table} LIMIT 5", conn)
        print(df.columns.tolist())
    except Exception as e:
        print(table, e)

conn.close()