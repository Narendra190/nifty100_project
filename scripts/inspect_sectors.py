from pathlib import Path
from src.reports.tearsheet import _load_company_data
import sqlite3, pandas as pd

c,ratios,_,_ = _load_company_data()
conn = sqlite3.connect(Path('nifty100.db'))
sectors = pd.read_sql_query('SELECT * FROM sectors_clean', conn)
conn.close()
print('unique broad_sector count:', sectors['broad_sector'].nunique())
print(sectors['broad_sector'].unique())
print('\ncompanies with broad_sector counts:')
merged = c.merge(sectors[['company_id','broad_sector']], on='company_id', how='left')
print('unique in merged:', merged['broad_sector'].nunique())
print(merged['broad_sector'].value_counts())
