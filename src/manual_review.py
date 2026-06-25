import sqlite3

conn = sqlite3.connect("../nifty100.db")
cursor = conn.cursor()

print("===== 5 Random Companies =====")

cursor.execute("""
SELECT *
FROM companies
ORDER BY RANDOM()
LIMIT 5;
""")

for row in cursor.fetchall():
    print(row)

print("\n===== Year Coverage =====")

cursor.execute("""
SELECT
MIN(substr(date,1,4)),
MAX(substr(date,1,4))
FROM stock_prices;
""")

print(cursor.fetchone())

print("\n===== Companies with Less Than 5 Years =====")

cursor.execute("""
SELECT company_id,
       COUNT(DISTINCT substr(date,1,4)) AS years
FROM stock_prices
GROUP BY company_id
HAVING COUNT(DISTINCT substr(date,1,4)) < 5;
""")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(row)
else:
    print("All companies have at least 5 years of data.")