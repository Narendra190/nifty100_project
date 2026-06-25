CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT
);

CREATE TABLE sectors (
    sector_id INTEGER PRIMARY KEY,
    sector_name TEXT
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT,
    sector TEXT
);

CREATE TABLE IF NOT EXISTS stock_prices (
    company_id INTEGER,
    trade_date DATE,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER
);