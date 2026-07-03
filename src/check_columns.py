import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

profit = pd.read_sql("SELECT * FROM profitandloss_clean LIMIT 1", conn)
balance = pd.read_sql("SELECT * FROM balancesheet_clean LIMIT 1", conn)
cashflow = pd.read_sql("SELECT * FROM cashflow_clean LIMIT 1", conn)

print("Profit & Loss Columns")
print(profit.columns.tolist())

print("\nBalance Sheet Columns")
print(balance.columns.tolist())

print("\nCash Flow Columns")
print(cashflow.columns.tolist())

conn.close()
