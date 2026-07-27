import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("""
SELECT DISTINCT broad_sector
FROM sectors_clean
ORDER BY broad_sector
""")

print(cursor.fetchall())

conn.close()