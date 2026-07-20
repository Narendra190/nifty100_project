import sqlite3
conn = sqlite3.connect('nifty100.db')
print(conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall())
for name in ['companies', 'financial_ratios', 'analysis_clean', 'prosandcons_clean']:
    print('---' + name + '---')
    print(conn.execute(f'PRAGMA table_info({name})').fetchall())
    print(conn.execute(f'SELECT * FROM {name} LIMIT 3').fetchall())
conn.close()
