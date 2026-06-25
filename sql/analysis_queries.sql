SELECT COUNT(*) AS total_companies
FROM companies;

SELECT COUNT(*) AS total_records
FROM stock_prices;

SELECT *
FROM companies
WHERE company_name IS NULL;

SELECT company,
       close_price
FROM stock_prices
ORDER BY close_price DESC
LIMIT 10;

SELECT AVG(close_price) AS avg_close_price
FROM stock_prices;

SELECT
    c.company_name,
    s.date,
    s.close_price
FROM companies c
JOIN stock_prices s
ON c.company_name = s.company
LIMIT 20;