import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM companies_clean")
print("Companies:", cursor.fetchone()[0])

cursor.execute("""
SELECT company_id, company_name
FROM companies_clean
LIMIT 5
""")

print(cursor.fetchall())

conn.close()