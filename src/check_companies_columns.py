import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

companies = pd.read_sql(
    "SELECT * FROM companies_clean LIMIT 1",
    conn
)

print("Companies Table Columns:")
print(companies.columns.tolist())

conn.close()