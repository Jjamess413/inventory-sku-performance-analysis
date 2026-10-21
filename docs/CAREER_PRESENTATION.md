# Project presentation notes

Use this project under **Projects**, separately from employment history. The source is public UCI data, not Shangpin Yitai data. Stock assumptions are synthetic.

## Resume project bullets

- Developed a reproducible SQL/Python retail analysis covering 511,035 transaction lines and 3,789 SKUs, combining ABC segmentation, monthly growth, credit review and calendar-based demand screening.
- Built an offline interactive dashboard that supports product search and filtered review queues; identified that 825 SKUs contribute 80.02% of gross sales and investigated an exceptional sale/credit offset candidate.

The Power BI component can be described as **“built a three-page native Power BI report with a four-table model and 24 DAX measures; reconciled the refreshed executive overview against SQL control totals.”** The actual Windows screenshot supports this scope. All-page interaction testing is not yet recorded. No realised business improvement is claimed.

## Sixty-second introduction

I built a retail SKU and inventory review case study using public transaction data from a UK-based retailer. The analysis covers twelve complete months and 3,789 products. I used SQL and Python to define the sales population, preserve credits and repeated entries, rank products and build an ABC classification.

One finding was that about 22% of products contributed 80% of gross sales. I also investigated a volume-leading product affected by a very large positive entry and an opposite credit on the same day, which shows why gross volume should not automatically become a replenishment recommendation.

The dashboard separates historical performance from a clearly labelled synthetic stock scenario. My proposed next step would be to validate actual stock and supplier data, resolve the exceptional entries and then test a small, monitored inventory review process.

## Evidence to have open

| Discussion | Evidence |
| --- | --- |
| Sales population and exclusions | data documentation, cleaning decisions and row reconciliation |
| ABC and window functions | SQL views, ABC summary and dashboard |
| Credit anomaly | SKU credit review and same-day offset candidates |
| Monthly performance | monthly_performance.csv and SQL 04 |
| Stock assumptions | scenario label, KPI definitions and blank quantities for manual-review items |
| Reproducibility | build scripts, business-rule tests and validation reports |

## Questions to practise later

1. Why retain credits separately from gross sales?
2. Why is sales contribution different from product profitability?
3. Why do zero-sale calendar days matter in daily-demand estimates?
4. What does the threshold-crossing ABC policy do?
5. Why can a high-volume entry require manual investigation?
6. Why does the fixed stock scenario have no historical country/date slicer?
7. What would you collect before claiming reduced stockouts or lower costs?

Learning is intentionally scheduled after delivery at James's request. These prompts are not a record of independent answers already assessed.
