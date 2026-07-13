import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql("""
SELECT *
FROM peer_percentiles
WHERE metric='return_on_equity_pct'
ORDER BY percentile_rank DESC
LIMIT 10
""", conn)

print(df)

conn.close()