import pandas as pd
import sqlite3
import os

conn = sqlite3.connect("nifty100.db")

files = {
    "companies": "data/processed/companies_clean.xlsx",
    "balancesheet": "data/processed/balancesheet_clean.xlsx",
    "cashflow": "data/processed/cashflow_clean.xlsx",
    "stock_prices": "data/processed/stock_prices_clean.xlsx"
}

for table_name, file_path in files.items():
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"{table_name} loaded successfully!")
    else:
        print(f"File not found: {file_path}")

conn.close()

print("All available tables loaded into SQLite!")




