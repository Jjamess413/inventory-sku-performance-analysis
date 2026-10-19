# Cleaning decisions

## Reporting population

Use 1 December 2010–30 November 2011. The source ends part-way through December 2011, so that final partial month is outside the model. This avoids comparing nine December days with complete months.

Only SKUs with an included positive sale in the reporting period enter the product model. Sixteen in-period credit entries have no positive-sale SKU in that cohort and are separately counted. The signed transaction value therefore describes this cohort rather than the retailer's complete ledger.

| Row reconciliation | Rows |
| --- | ---: |
| Original workbook | 541,909 |
| Outside reporting period | 25,525 |
| In-period excluded entries | 5,333 |
| In-period credit entries outside positive-sale SKU cohort | 16 |
| Model transactions | 511,035 |

These four mutually exclusive destinations sum to the source row count. `reports/data_quality.json` records the source-wide and model-specific counts.

## Decisions that affect the answer

1. **Missing customer IDs:** retain otherwise valid transactions. The analysis concerns products and operations, so customer identity is unnecessary. CustomerID is omitted from all exported model tables.
2. **Missing descriptions:** retain valid sales and resolve a product label from the latest nonblank observed description by the reporting cutoff. A SKU is a key; a description is an attribute that may change.
3. **Merchandise proxy:** include codes matching five digits followed by zero to two letters. Entries such as postage, discounts and manual adjustments are excluded from merchandise metrics. This pattern is an assumption, not a verified product master.
4. **Sales:** positive quantity, positive price, valid merchandise code and invoice without the cancellation prefix.
5. **Cancellations/credits:** negative quantity, positive price, valid merchandise code and a cancellation-prefixed invoice. Keep them as negative entries. Do not infer a confirmed physical return, refund or original sale link.
6. **Other quantity/price combinations:** exclude with an explicit reason rather than silently treating them as sales.
7. **Exact repeats:** flag and retain. The source lacks a unique invoice-line ID; identical rows may be legitimate repeated lines. Removing them without evidence is a separate assumption. Gross sales would be £9,632,333.24 if flagged repeated sale rows were removed, versus £9,655,544.63 under the retained-row policy.
8. **Currency:** use integer GBP pence. Round each unit price half up before multiplication. Four source entries have subpenny precision; the reviewed merchandise population does not require a different currency treatment. GBP is not relabelled as AUD.
9. **Outliers:** preserve and investigate. Same-day, same-SKU, same-price, equal-and-opposite quantities are offset candidates, not confirmed matches. They are reported without automatically deleting or netting order demand.

## Inventory assumptions

Recent sales are estimated over the final 90 calendar days, including zero-sale days after the first observed positive sale. The source does not identify product availability, shop closures or lost sales. A zero can therefore represent more than zero demand.

The normal-demand safety-stock baseline is withheld for no recent sales, fewer than 90 observed days, fewer than ten active sale days, or at least half of recent volume on one day. These receive a manual review status and a blank suggested order quantity. Passing this screen does not prove the distribution is normal or stationary.

All stock balances and lead times are generated assumptions with an explicit data-nature column. There are no invented observed stockouts, realised savings, supplier performance results or financial inventory-turnover figures.

## Validation

The build checks reconciliation, keys, database integrity, sales and unit totals, ABC coverage, synthetic labels, manual-review behaviour and calendar completeness. Hand-calculated fixtures additionally test cancellations, duplicates, rounding, threshold crossings and zero-sale days. The current validation JSON records the actual execution environment and check results.
