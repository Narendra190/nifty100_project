import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

profit = pd.read_sql("SELECT company_id, year FROM profitandloss_clean", conn)
balance = pd.read_sql("SELECT company_id, year FROM balancesheet_clean", conn)
cashflow = pd.read_sql("SELECT company_id, year FROM cashflow_clean", conn)

missing = 0

for _, row in profit.iterrows():

    b = balance[
        (balance.company_id == row.company_id) &
        (balance.year == row.year)
    ]

    c = cashflow[
        (cashflow.company_id == row.company_id) &
        (cashflow.year == row.year)
    ]

    if b.empty or c.empty:
        missing += 1

print("Missing Company-Year Records:", missing)

conn.close()