let
    Source = fxLoadCsv("dim_sku.csv", {
        {"sku", type text}, {"description", type text}, {"first_sale_date", type date},
        {"last_sale_date", type date}, {"abc_class", type text}
    }),
    TrimmedKeys = Table.TransformColumns(Source, {{"sku", Text.Trim, type text}}),
    Output = if Table.RowCount(TrimmedKeys) <> Table.RowCount(Table.Distinct(TrimmedKeys, {"sku"}))
        then error "DimSKU requires one row per SKU. Investigate duplicate keys."
        else TrimmedKeys
in
    Output
