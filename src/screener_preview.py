import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

query = """
SELECT company_id,
       MAX(return_on_equity_pct) AS roe,
       MIN(debt_to_equity) AS debt_to_equity
FROM financial_ratios
WHERE return_on_equity_pct > 15
AND debt_to_equity < 1
GROUP BY company_id;
"""

df = pd.read_sql(query, conn)

print(df)

print()

print("Companies Found:", len(df))

conn.close()