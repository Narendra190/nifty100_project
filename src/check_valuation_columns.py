import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
market = pd.read_sql("SELECT * FROM market_cap_clean", conn)
companies = pd.read_sql("SELECT * FROM companies_clean", conn)
sectors = pd.read_sql("SELECT * FROM sectors_clean", conn)

conn.close()

market = (
    market.sort_values("year")
          .drop_duplicates(subset="company_id", keep="last")
)

df = ratios.merge(
    market,
    on="company_id",
    how="left"
)

df = df.merge(
    sectors,
    on="company_id",
    how="left"
)

df = df.merge(
    companies,
    on="company_id",
    how="left"
)

print(df.columns.tolist())