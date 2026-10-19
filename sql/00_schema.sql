-- SQL dialect: SQLite 3.25+. Python registers SQRT and CEIL for portability.
CREATE TABLE parameters (
    analysis_start TEXT, analysis_end TEXT, lookback_start TEXT,
    lookback_days INTEGER, minimum_active_days INTEGER, service_z REAL,
    order_cycle_days INTEGER, excess_cover_days INTEGER
);
CREATE TABLE dim_date (
    date TEXT PRIMARY KEY, month TEXT NOT NULL, year INTEGER NOT NULL,
    month_number INTEGER NOT NULL, day_of_week INTEGER NOT NULL
);
CREATE TABLE dim_sku (
    sku TEXT PRIMARY KEY, description TEXT NOT NULL,
    first_sale_date TEXT NOT NULL, last_sale_date TEXT NOT NULL
);
CREATE TABLE fact_transactions (
    source_line_id INTEGER PRIMARY KEY, invoice_no TEXT NOT NULL,
    sku TEXT NOT NULL REFERENCES dim_sku(sku), date TEXT NOT NULL REFERENCES dim_date(date),
    quantity INTEGER NOT NULL, unit_price_pence INTEGER NOT NULL CHECK (unit_price_pence > 0),
    revenue_pence INTEGER NOT NULL, country TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('sale', 'cancellation')),
    is_exact_repeat INTEGER NOT NULL CHECK (is_exact_repeat IN (0, 1)),
    CHECK (revenue_pence = quantity * unit_price_pence)
);
CREATE TABLE synthetic_inventory_snapshot (
    sku TEXT PRIMARY KEY REFERENCES dim_sku(sku), snapshot_date TEXT NOT NULL,
    on_hand_units INTEGER NOT NULL CHECK (on_hand_units >= 0),
    on_order_units INTEGER NOT NULL CHECK (on_order_units >= 0),
    reserved_units INTEGER NOT NULL CHECK (reserved_units BETWEEN 0 AND on_hand_units),
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0),
    data_nature TEXT NOT NULL CHECK (data_nature = 'SYNTHETIC_SCENARIO')
);
CREATE INDEX ix_transactions_sku_date ON fact_transactions(sku, date);
CREATE INDEX ix_transactions_type_date ON fact_transactions(transaction_type, date);
