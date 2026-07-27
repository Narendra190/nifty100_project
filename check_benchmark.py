import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    peer_group_name,
    company_id,
    is_benchmark
FROM peer_groups_clean
ORDER BY peer_group_name, is_benchmark DESC
LIMIT 30
""")

for row in cursor.fetchall():
    print(row)

conn.close()