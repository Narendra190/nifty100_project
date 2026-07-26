import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

for table in [
    "profitandloss_clean",
    "balancesheet_clean",
    "cashflow_clean"
]:
    print(f"\n===== {table} =====")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        print(row)

conn.close()