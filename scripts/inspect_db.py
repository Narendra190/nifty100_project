import sqlite3
import pandas as pd

conn = sqlite3.connect('nifty100.db')
print(pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn))
print('\nsectors_clean schema:\n')
try:
    print(pd.read_sql_query("PRAGMA table_info('sectors_clean')", conn))
except Exception as e:
    print('Error reading sectors_clean:', e)

print('\ncompanies schema:\n')
print(pd.read_sql_query("PRAGMA table_info('companies_clean')", conn))
conn.close()
