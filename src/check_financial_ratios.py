import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM financial_ratios")

print("Financial Ratios Rows:", cursor.fetchone()[0])

conn.close()