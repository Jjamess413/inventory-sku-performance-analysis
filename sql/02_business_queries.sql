-- Run individual statements after: python scripts/build.py
-- SQL statements can be copied into DB Browser for SQLite.

-- 1. Which products generate the most revenue? SELECT, WHERE, INNER JOIN.
SELECT s.sku, p.description, SUM(s.quantity) AS units_sold,
       ROUND(SUM(s.revenue_pence) / 100.0, 2) AS gross_sales_gbp
FROM v_sales AS s
INNER JOIN dim_sku AS p ON s.sku = p.sku
WHERE s.date BETWEEN (SELECT analysis_start FROM parameters) AND (SELECT analysis_end FROM parameters)
GROUP BY s.sku, p.description
ORDER BY gross_sales_gbp DESC, s.sku LIMIT 10;

-- 2. Highest and lowest volume: compare this ranking with revenue ranking.
SELECT sku, units_sold, gross_revenue_pence / 100.0 AS gross_sales_gbp
FROM v_abc ORDER BY units_sold DESC, sku LIMIT 10;

SELECT sku, units_sold, gross_revenue_pence / 100.0 AS gross_sales_gbp
FROM v_abc ORDER BY units_sold, sku LIMIT 10;

-- 3. HAVING filters groups after aggregation; WHERE filters source rows.
SELECT sku, SUM(quantity) AS units_sold, COUNT(DISTINCT invoice_no) AS orders
FROM v_sales GROUP BY sku HAVING SUM(quantity) >= 10000
ORDER BY units_sold DESC, sku;

-- 4. ABC prioritisation; the CTE/window calculation is in 01_analysis_views.sql.
SELECT abc_class, COUNT(*) AS sku_count, SUM(units_sold) AS units_sold,
       SUM(gross_revenue_pence) / 100.0 AS gross_sales_gbp,
       ROUND(100.0 * SUM(gross_revenue_pence) / (SELECT SUM(revenue_pence) FROM v_sales), 2) AS sales_share_pct
FROM v_abc GROUP BY abc_class ORDER BY abc_class;

-- 5. Monthly changes: compare complete calendar months only.
WITH monthly AS (
    SELECT SUBSTR(date, 1, 7) AS month, SUM(quantity) AS units_sold,
           SUM(revenue_pence) AS gross_revenue_pence
    FROM v_sales GROUP BY SUBSTR(date, 1, 7)
), compared AS (
    SELECT *, LAG(gross_revenue_pence) OVER (ORDER BY month) AS prior_month_revenue
    FROM monthly
)
SELECT month, units_sold, gross_revenue_pence / 100.0 AS gross_sales_gbp,
       ROUND(100.0 * (gross_revenue_pence - prior_month_revenue)
             / NULLIF(prior_month_revenue, 0), 2) AS month_on_month_pct
FROM compared ORDER BY month;

-- 6. Scenario risk queue; these are NOT observed stockouts or excess stock.
SELECT i.sku, s.description, i.abc_class, i.scenario_flag, i.demand_status,
       i.on_hand_units, i.inventory_position_units, i.safety_stock_units,
       i.reorder_point_units, i.suggested_order_units, ROUND(i.days_cover, 1) AS days_cover
FROM v_inventory_policy AS i
LEFT JOIN dim_sku AS s ON i.sku = s.sku
WHERE i.scenario_flag IN ('Reorder review', 'Excess cover review')
ORDER BY i.abc_class, i.gross_revenue_pence DESC, i.sku;

-- 7. Gross sales and credit/cancellation entries are distinct concepts.
SELECT transaction_type, COUNT(*) AS transaction_lines, SUM(quantity) AS signed_units,
       SUM(revenue_pence) / 100.0 AS signed_transaction_value_gbp
FROM fact_transactions GROUP BY transaction_type;
