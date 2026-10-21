-- Calendar-month totals; use integer pence until final display.
-- LAG means the previous row. The existing model covers twelve consecutive months.
-- Apply a one-month display filter in the outer query, after LAG is calculated.
WITH monthly_totals AS (
    SELECT SUBSTR(date, 1, 7) AS sales_month,
           SUM(quantity) AS units_sold,
           SUM(revenue_pence) AS gross_sales_pence
    FROM v_sales
    GROUP BY SUBSTR(date, 1, 7)
), monthly_comparison AS (
    SELECT sales_month, units_sold, gross_sales_pence,
           LAG(units_sold) OVER (ORDER BY sales_month) AS previous_month_units_sold,
           LAG(gross_sales_pence) OVER (ORDER BY sales_month) AS previous_month_sales_pence
    FROM monthly_totals
)
SELECT sales_month,
       units_sold, previous_month_units_sold,
       ROUND(100.0 * (units_sold - previous_month_units_sold)
             / NULLIF(previous_month_units_sold, 0), 2) AS units_mom_pct,
       ROUND(gross_sales_pence / 100.0, 2) AS gross_sales_gbp,
       ROUND(previous_month_sales_pence / 100.0, 2) AS previous_month_sales_gbp,
       ROUND(100.0 * (gross_sales_pence - previous_month_sales_pence)
             / NULLIF(previous_month_sales_pence, 0), 2) AS sales_mom_pct
FROM monthly_comparison
ORDER BY sales_month;
