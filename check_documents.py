import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM documents_clean
LIMIT 5
""")

for row in cursor.fetchall():
    print(row)

conn.close()