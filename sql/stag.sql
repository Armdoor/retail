CREATE TABLE stg_transactions AS
SELECT
    Invoice         AS invoice_id,
    StockCode       AS stock_code,
    LOWER(Description) AS description,
    CAST(Quantity AS INT) AS quantity,
    CAST(Price AS NUMERIC) AS unit_price,
    CAST("Customer ID" AS INT) AS customer_id,
    Country         AS country,
    CAST(Date || ' ' || Time AS TIMESTAMP) AS order_datetime,
    Quantity * Price AS line_revenue
FROM raw_transactions
WHERE customer_id IS NOT NULL
  AND quantity > 0
  AND unit_price > 0;