import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

tables = [
    "peer_groups_clean",
    "market_cap_clean",
    "documents_clean"
]

for table in tables:
    print(f"\n===== {table} =====")
    cursor.execute(f"PRAGMA table_info({table})")
    for row in cursor.fetchall():
        print(row)

conn.close()