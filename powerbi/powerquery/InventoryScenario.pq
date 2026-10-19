let
    Source = fxLoadCsv("inventory_scenario.csv", {
        {"sku", type text}, {"snapshot_date", type date}, {"data_nature", type text},
        {"on_hand_units", Int64.Type}, {"on_order_units", Int64.Type}, {"reserved_units", Int64.Type},
        {"lead_time_days", Int64.Type}, {"inventory_position_units", Int64.Type},
        {"mean_daily_units", type number}, {"std_daily_units", type number}, {"days_cover", type number},
        {"safety_stock_units", Int64.Type}, {"reorder_point_units", Int64.Type},
        {"target_stock_units", Int64.Type}, {"suggested_order_units", Int64.Type},
        {"demand_status", type text}, {"scenario_flag", type text}, {"abc_class", type text}
    }),
    Selected = Table.SelectColumns(Source, {
        "sku", "snapshot_date", "data_nature", "on_hand_units", "on_order_units", "reserved_units",
        "lead_time_days", "inventory_position_units", "mean_daily_units", "std_daily_units", "days_cover",
        "safety_stock_units", "reorder_point_units", "target_stock_units", "suggested_order_units",
        "demand_status", "scenario_flag", "abc_class"
    }),
    InvalidNature = Table.SelectRows(Selected, each [data_nature] <> "SYNTHETIC_SCENARIO"),
    Output = if Table.RowCount(InvalidNature) > 0
        then error "Inventory rows must retain their synthetic scenario label."
        else Selected
in
    Output
