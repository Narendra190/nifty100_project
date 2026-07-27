import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("""
SELECT DISTINCT peer_group_name
FROM peer_groups_clean
ORDER BY peer_group_name
""")

for row in cursor.fetchall():
    print(row[0])

conn.close()