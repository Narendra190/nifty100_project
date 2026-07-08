import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

conn.close()

df = df.sort_values(
    "composite_quality_score",
    ascending=False
)

df.to_excel(
    "output/screener_output.xlsx",
    index=False
)

print("Excel Export Completed")