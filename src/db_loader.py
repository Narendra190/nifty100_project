import pandas as pd
import sqlite3

conn = sqlite3.connect("nifty100.db")

df = pd.read_excel("data/processed/companies_clean.xlsx")

df.to_sql(
    "companies",
    conn,
    if_exists="replace",
    index=False
)
print("Database created successfully")
print("Companies data loaded!")
print(df.columns.tolist())

conn.close()

