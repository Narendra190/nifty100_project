SELECT COUNT(*) FROM companies;

SELECT COUNT(*) FROM stock_prices;

SELECT AVG(close_price) FROM stock_prices;

SELECT MAX(close_price) FROM stock_prices;

SELECT MIN(close_price) FROM stock_prices;

SELECT company_id, close_price
FROM stock_prices
ORDER BY close_price DESC
LIMIT 10;

SELECT MIN(date), MAX(date)
FROM stock_prices;

SELECT SUM(volume)
FROM stock_prices;

SELECT company_id, COUNT(*)
FROM stock_prices
GROUP BY company_id;

SELECT *
FROM companies
ORDER BY RANDOM()
LIMIT 5;