import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql(
    "SELECT * FROM documents_clean LIMIT 5",
    conn
)

print(df.columns.tolist())

conn.close()