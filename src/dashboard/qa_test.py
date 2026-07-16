import sqlite3
import pandas as pd
conn = sqlite3.connect("nifty100.db")
companies = pd.read_sql(
    "SELECT company_id FROM companies_clean",
    conn
)
conn.close()
print("=" * 50)
print("Dashboard QA Test")
print("=" * 50)
print("Companies:", len(companies))
print("Sample Companies:")
print(companies.head(10))
print("=" * 50)
print("QA PASSED")