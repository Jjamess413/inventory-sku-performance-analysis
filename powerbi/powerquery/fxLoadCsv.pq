// Create pDataFolder as a Text parameter with a trailing path separator.
// Create this function as one blank query named fxLoadCsv.
(FileName as text, ColumnTypes as list) as table =>
let
    Source = Csv.Document(
        File.Contents(pDataFolder & FileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    BlankToNull = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),
    Typed = Table.TransformColumnTypes(BlankToNull, ColumnTypes, "en-AU")
in
    Typed
