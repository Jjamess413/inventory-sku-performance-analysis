-- Investigate exceptional gross demand without claiming confirmed return links.
SELECT sku, date, ABS(quantity) AS units_per_line, unit_price_pence / 100.0 AS unit_price_gbp,
       SUM(CASE WHEN transaction_type = 'sale' THEN 1 ELSE 0 END) AS positive_lines,
       SUM(CASE WHEN transaction_type = 'cancellation' THEN 1 ELSE 0 END) AS negative_lines
FROM fact_transactions
GROUP BY sku, date, ABS(quantity), unit_price_pence
HAVING SUM(CASE WHEN transaction_type = 'sale' THEN 1 ELSE 0 END) > 0
   AND SUM(CASE WHEN transaction_type = 'cancellation' THEN 1 ELSE 0 END) > 0
ORDER BY units_per_line * unit_price_gbp DESC, sku, date;

-- Contrast gross merchandising activity with signed transaction value.
SELECT sku,
       SUM(CASE WHEN transaction_type = 'sale' THEN quantity ELSE 0 END) AS gross_units,
       -SUM(CASE WHEN transaction_type = 'cancellation' THEN quantity ELSE 0 END) AS credited_units,
       SUM(CASE WHEN transaction_type = 'sale' THEN revenue_pence ELSE 0 END) / 100.0 AS gross_sales_gbp,
       SUM(revenue_pence) / 100.0 AS signed_transaction_value_gbp
FROM fact_transactions
WHERE sku = '23166'
GROUP BY sku;
