-- Positive, priced merchandise sales; cancelled quantities remain in the fact table.
CREATE VIEW v_sales AS
SELECT * FROM fact_transactions WHERE transaction_type = 'sale';

-- ABC uses full-period gross merchandise sales, in GBP minor units.
-- The item crossing each threshold stays in the higher-priority class.
-- Equal revenue is ordered by SKU to keep results reproducible.
CREATE VIEW v_abc AS
WITH sku_totals AS (
    SELECT sku, SUM(quantity) AS units_sold, SUM(revenue_pence) AS gross_revenue_pence,
           COUNT(DISTINCT invoice_no) AS sales_orders
    FROM v_sales GROUP BY sku
), running AS (
    SELECT *, SUM(gross_revenue_pence) OVER () AS all_revenue_pence,
           SUM(gross_revenue_pence) OVER (
               ORDER BY gross_revenue_pence DESC, sku
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_revenue_pence,
           ROW_NUMBER() OVER (ORDER BY gross_revenue_pence DESC, sku) AS revenue_rank
    FROM sku_totals
)
SELECT *, 1.0 * gross_revenue_pence / NULLIF(all_revenue_pence, 0) AS revenue_share,
       1.0 * cumulative_revenue_pence / NULLIF(all_revenue_pence, 0) AS cumulative_share,
       CASE
           WHEN 1.0 * (cumulative_revenue_pence - gross_revenue_pence) / all_revenue_pence < 0.80 THEN 'A'
           WHEN 1.0 * (cumulative_revenue_pence - gross_revenue_pence) / all_revenue_pence < 0.95 THEN 'B'
           ELSE 'C'
       END AS abc_class
FROM running;

-- The calendar supplies zero-sale days. Days before the first observed sale
-- are omitted; the first observed sale is only a proxy for product availability.
CREATE VIEW v_daily_demand AS
WITH daily_sales AS (
    SELECT sku, date, SUM(quantity) AS daily_units
    FROM v_sales
    WHERE date >= (SELECT lookback_start FROM parameters)
    GROUP BY sku, date
)
SELECT s.sku, d.date, COALESCE(t.daily_units, 0) AS daily_units
FROM dim_sku AS s
CROSS JOIN dim_date AS d
LEFT JOIN daily_sales AS t ON s.sku = t.sku AND d.date = t.date
WHERE d.date >= (SELECT lookback_start FROM parameters)
  AND d.date >= s.first_sale_date;

CREATE VIEW v_demand_stats AS
WITH moments AS (
    SELECT sku, COUNT(*) AS observation_days, SUM(daily_units) AS recent_units,
           SUM(CASE WHEN daily_units > 0 THEN 1 ELSE 0 END) AS active_sales_days,
           MAX(daily_units) AS largest_day_units,
           1.0 * MAX(daily_units) / NULLIF(SUM(daily_units), 0) AS largest_day_share,
           1.0 * SUM(daily_units) / COUNT(*) AS mean_daily_units,
           SUM(1.0 * daily_units * daily_units) AS sum_squared_units
    FROM v_daily_demand GROUP BY sku
)
SELECT *, CASE WHEN observation_days > 1 THEN
           SQRT(MAX(0.0, (sum_squared_units - 1.0 * recent_units * recent_units / observation_days)
                          / (observation_days - 1)))
           ELSE 0.0 END AS std_daily_units,
       CASE WHEN recent_units = 0 THEN 'No recent sales'
            WHEN observation_days < (SELECT lookback_days FROM parameters) THEN 'Limited history'
            WHEN active_sales_days < (SELECT minimum_active_days FROM parameters) THEN 'Intermittent sales'
            WHEN largest_day_share >= 0.50 THEN 'Concentrated sales'
            ELSE 'Eligible for baseline' END AS demand_status
FROM moments;

-- Every stock quantity and supplier lead time below is a synthetic assumption.
-- Safety stock estimates are a baseline under stationary, independent daily sales
-- and constant lead time. They are not a service-level guarantee.
CREATE VIEW v_inventory_policy AS
WITH base AS (
    SELECT s.*, d.observation_days, d.recent_units, d.active_sales_days,
           d.mean_daily_units, d.std_daily_units, d.largest_day_units, d.largest_day_share, d.demand_status,
           a.abc_class, a.gross_revenue_pence,
           s.on_hand_units + s.on_order_units - s.reserved_units AS inventory_position_units,
           1.0 * (s.on_hand_units - s.reserved_units) / NULLIF(d.mean_daily_units, 0) AS days_cover,
           CASE WHEN d.demand_status = 'Eligible for baseline' THEN
               CAST(CEIL(p.service_z * d.std_daily_units * SQRT(s.lead_time_days)) AS INTEGER)
           END AS safety_stock_units,
           p.service_z, p.order_cycle_days, p.excess_cover_days
    FROM synthetic_inventory_snapshot AS s
    INNER JOIN v_demand_stats AS d ON s.sku = d.sku
    INNER JOIN v_abc AS a ON s.sku = a.sku
    CROSS JOIN parameters AS p
), thresholds AS (
    SELECT *, CASE WHEN safety_stock_units IS NOT NULL THEN
               CAST(CEIL(mean_daily_units * lead_time_days + safety_stock_units) AS INTEGER)
           END AS reorder_point_units,
           CASE WHEN safety_stock_units IS NOT NULL THEN
               CAST(CEIL(mean_daily_units * (lead_time_days + order_cycle_days)
                    + service_z * std_daily_units * SQRT(lead_time_days + order_cycle_days)) AS INTEGER)
           END AS target_stock_units
    FROM base
)
SELECT *, CASE WHEN inventory_position_units <= reorder_point_units
               THEN MAX(0, target_stock_units - inventory_position_units)
               WHEN reorder_point_units IS NOT NULL THEN 0 END AS suggested_order_units,
       CASE WHEN demand_status <> 'Eligible for baseline' THEN 'Manual review'
            WHEN inventory_position_units <= reorder_point_units THEN 'Reorder review'
            WHEN days_cover > excess_cover_days THEN 'Excess cover review'
            ELSE 'Within scenario policy' END AS scenario_flag
FROM thresholds;
