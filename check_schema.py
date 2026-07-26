import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

for table in ["companies_clean", "sectors_clean", "financial_ratios"]:
    print(f"\n===== {table} =====")

    cursor.execute(f"PRAGMA table_info({table})")

    for row in cursor.fetchall():
        print(row)

conn.close()