import sqlite3

conn = sqlite3.connect("../nifty100.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_key_check")

rows = cursor.fetchall()

if len(rows) == 0:
    print("✅ Foreign Key Check Passed (0 errors)")
else:
    print("❌ Foreign Key Errors:")
    for row in rows:
        print(row)

conn.close()