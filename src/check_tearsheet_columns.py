import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

tables = [
    "profitandloss_clean",
    "balancesheet_clean",
    "cashflow_clean",
    "financial_ratios",
    "companies_clean"
]

for table in tables:
    print(f"\n===== {table} =====")
    df = pd.read_sql(f"SELECT * FROM {table} LIMIT 3", conn)
    print(df.columns.tolist())

conn.close()