# KPI definitions and planning assumptions

Historical metrics cover the positive-sale SKU cohort during 1 December 2010–30 November 2011. Planning metrics use the fixed 30 November 2011 snapshot and 2 September–30 November lookback. Sales values are GBP. Stock metrics are units unless stated otherwise.

| Metric | Definition | Qualification |
| --- | --- | --- |
| Gross merchandise sales | Sum of quantity × unit price for included positive sales | Before cancellation/credit entries; no profit or cash interpretation |
| Gross units | Sum of positive sale quantities | Ordered units; not confirmed shipped or consumed units |
| Sales orders | Distinct sale invoices | Not the number of invoice lines |
| Cancellation/credit value | Negative of the sum of included negative-entry values | Positive displayed value; unmatched to original invoices |
| Signed transaction value | Gross sales minus included cancellation/credit value | A cohort transaction total, not recognised accounting revenue |
| Active SKUs | Distinct SKUs with positive sales | Not a complete inventory master |
| ABC class | Descending full-period gross sales contribution, A to 80%, B to 95%, C remainder | Threshold-crossing item stays in the higher-priority class; ties ordered by SKU |
| Average daily units | Recent positive units ÷ observed calendar days | Includes zero-sale days after first observed sale |
| Daily standard deviation | Sample standard deviation of the same daily quantities, denominator n−1 | Variability of observed order sales, not forecast error |
| Inventory position | Synthetic on-hand + on-order − reserved | Assumes no additional backorders and no double subtraction of reservations |
| Days of cover | (Synthetic on-hand − reserved) ÷ average daily units | Blank when mean is zero; ignores inbound timing |
| Safety stock | ceil(1.645 × daily standard deviation × sqrt(lead-time days)) | Fixed-lead-time, independent stationary daily-demand approximation; eligible SKUs only |
| Reorder point | ceil(mean daily units × lead time + rounded safety stock) | Trigger for continuously monitored min/max scenario |
| Target stock | ceil(mean × (lead time + order cycle) + 1.645 × std × sqrt(lead time + order cycle)) | Illustrative order-up-to quantity with seven-day cycle coverage |
| Suggested order | max(0, target stock − inventory position), only when inventory position ≤ reorder point | A scenario review quantity; blank for manual-review demand |
| Excess-cover review | Eligible, not due for reorder, with over 90 days of available on-hand cover | Threshold is an editable heuristic, not observed overstock |

## Assumption controls

`config.json` owns the period, lookback, service factor, minimum active days, order cycle and excess-cover threshold. Rerun the pipeline after changes. No Power BI slicer should imply that these stored policy outputs dynamically recalculate.

The factor 1.645 corresponds approximately to a one-sided 95% normal quantile. It is an illustrative cycle-service target under restrictive assumptions, not a measured fill rate or a proven achieved service level. Lead times of 7, 14 and 21 days are synthetic. No supplier reliability, minimum order quantity, pack size or purchasing budget constraints are modelled.

Ten active days and the 50% single-day concentration cutoff are conservative teaching heuristics. Product introductions, intermittent demand, wholesale orders, seasonal shifts and unobserved stockouts need further investigation. Supplier lead-time variability would require a different uncertainty calculation.

## Measures intentionally unavailable

- Actual stockout, damage, loss and service-level rates: corresponding events are absent.
- Financial inventory turnover: COGS and observed average inventory value are absent.
- Gross profit, net profit and margin: product costs, fees and expense allocations are absent.
- Realised cost reduction or working-capital release: no implemented intervention or observed inventory ledger.

## Method references

- [MIT OpenCourseWare inventory lecture notes](https://ocw.mit.edu/courses/esd-260j-logistics-systems-fall-2006/pages/lecture-notes/) for probabilistic inventory and safety-stock concepts.
- [SQLite window functions](https://www.sqlite.org/windowfunctions.html) for cumulative ABC calculations and ranking.
- [Microsoft star-schema guidance](https://learn.microsoft.com/power-bi/guidance/star-schema) for the planned Power BI model.
