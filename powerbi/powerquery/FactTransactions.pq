let
    Source = fxLoadCsv("fact_transactions.csv", {
        {"source_line_id", Int64.Type}, {"invoice_no", type text}, {"sku", type text},
        {"date", type date}, {"quantity", Int64.Type}, {"unit_price_pence", Int64.Type},
        {"revenue_pence", Int64.Type}, {"country", type text},
        {"transaction_type", type text}, {"is_exact_repeat", Int64.Type}
    }),
    TrimmedKeys = Table.TransformColumns(Source, {
        {"sku", Text.Trim, type text}, {"invoice_no", Text.Trim, type text}
    }),
    Invalid = Table.SelectRows(TrimmedKeys, each
        [sku] = null or [sku] = "" or [unit_price_pence] <= 0
        or [revenue_pence] <> [quantity] * [unit_price_pence]
    ),
    Output = if Table.RowCount(Invalid) > 0
        then error "Unexpected transaction values. Review the pipeline output."
        else TrimmedKeys
in
    Output
