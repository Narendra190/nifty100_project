import sqlite3

conn = sqlite3.connect("../nifty100.db")
cursor = conn.cursor()

# Total companies
cursor.execute("SELECT COUNT(*) FROM companies")
print("Total companies:", cursor.fetchone()[0])

# Total stock price records
cursor.execute("SELECT COUNT(*) FROM stock_prices")
print("Total stock price records:", cursor.fetchone()[0])

# Average close price
cursor.execute("SELECT AVG(close_price) FROM stock_prices")
print("Average close price:", cursor.fetchone()[0])

conn.close()