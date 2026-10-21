# Data selection and lineage

## Candidates reviewed on 19 October 2026

| Dataset | Evidence and useful fields | Limitation for this project | Decision |
| --- | --- | --- | --- |
| [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) | Public transactions with item code, quantity, date and price; CC BY 4.0. Downloaded workbook verified: 541,909 rows and eight columns. | No stock ledger, supplier lead time or costs; historical UK data. | Selected. Enough real transaction complexity for SQL and a clearly separate stock scenario. |
| [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) | Catalogue lists 1,067,371 observations across two years; CC BY 4.0. | Similar missing inventory fields and a larger workbook. Source page reviewed; file not downloaded. | Useful later for multi-year trend work; unnecessary initial complexity. |
| [UCI Sales Transactions Weekly](https://archive.ics.uci.edu/dataset/396/sales+transactions+dataset+weekly) | Catalogue describes 811 product series with weekly quantities; CC BY 4.0. | No transaction prices or order-level records for revenue questions. Source page reviewed; file not downloaded. | Suitable for volume exercises, weaker for this portfolio scope. |
| [Kaggle Retail Store Inventory and Demand Forecasting, version 8](https://www.kaggle.com/datasets/atomicd/retail-store-inventory-and-demand-forecasting/versions/8) | Data card lists inventory, restocking, price and demand fields; card lists Apache 2.0. | The author explicitly describes the dataset as synthetic. File not downloaded or integrity-tested. | Useful for a fully synthetic demonstration; not selected as observed business data. |

## Source fields

| Original field | Model treatment | Nature |
| --- | --- | --- |
| InvoiceNo | Normalise to text; use cancellation prefix and invoice counts | Observed public identifier |
| StockCode | Text SKU; apply the documented merchandise-code proxy | Observed public identifier |
| Description | Trim; latest nonblank description within the analysis period becomes the SKU label | Observed text, transformed |
| Quantity | Signed whole units; classify positive sales and negative cancellation entries | Observed numeric field |
| InvoiceDate | Reporting date; preserve source ordering for choosing labels | Observed timestamp, transformed |
| UnitPrice | GBP unit price; round half up to integer pence | Observed numeric field, transformed |
| CustomerID | Omitted from all model tables and exports | Not needed for this analysis |
| Country | Retain for future sales filtering; not a warehouse or supplier location | Observed public geography |

## Derived and synthetic fields

| Field group | Origin | Use |
| --- | --- | --- |
| Sales values, ABC, daily means and standard deviations | Calculated from included source transactions | Historical analysis and baseline inputs |
| Calendar and zero-sale days | Reporting calendar joined to observed sales | Include zero-sale days after the first observed sale; availability remains unknown |
| On-hand, on-order and reserved quantities | Deterministic synthetic scenario | Illustrate a stock review queue |
| Lead times of 7, 14 or 21 days | Deterministic synthetic assumption | Illustrate supplier lead-time effects |
| Safety stock, reorder point and suggested order | Derived from observed-sales proxies plus synthetic assumptions | Hypothetical planning outputs, not observations |
| `data_nature` | Constant `SYNTHETIC_SCENARIO` on every stock row | Preserve the boundary in every export |

The scenario generator uses a stable SHA-256 hash of each SKU to assign coverage and lead-time assumptions. It is reproducible and does not estimate actual stock. Balances do not form a historical stock-flow ledger. Revenue cannot be used as a substitute for inventory carrying value or profit.

## Provenance and licence

The full download URL and reviewed SHA-256 checksums are in [config.json](../config.json). The build fails if the source bytes change. The source contains missing values despite a contradictory missing-value summary on its catalogue page; the downloaded workbook and [data-quality report](../reports/data_quality.json) are the authority for this analysis.

See [DATA_ATTRIBUTION.md](../DATA_ATTRIBUTION.md) for the citation, CC BY 4.0 link and adaptations. Raw and processed transaction files remain local; shareable aggregates and synthetic assumptions are committed.

## Portfolio export addition

The dashboard builder creates `data/processed/dim_sku_portfolio.csv` from the same 3,789-SKU dimension and materialised ABC analysis. It adds the fixed full-period revenue rank and a SKU/product display label for the authored Power BI report. The original `dim_sku.csv` is retained. The extended export contains no customer identifiers.
