import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql("""
SELECT
company_id,
return_on_equity_pct,
debt_to_equity,
composite_quality_score
FROM financial_ratios
WHERE return_on_equity_pct > 15
AND debt_to_equity < 1
ORDER BY composite_quality_score DESC
LIMIT 5
""", conn)
print(df)
conn.close()