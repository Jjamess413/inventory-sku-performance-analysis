# Inventory & SKU Performance Analysis

Prioritise retail products by sales contribution and build a transparent stock review process.

**Status: SQL analysis foundation validated. Power BI dashboard and independent owner walkthrough pending.**

This portfolio case study uses public UK retail transactions. All stock balances, reservations, purchase quantities and supplier lead times are **synthetic assumptions**. It demonstrates analytical methods relevant to my business analysis experience; it does not use Shangpin Yitai's data or claim an implemented business outcome.

## Business questions

1. Which SKUs contribute the most revenue and sales volume?
2. How can ABC classification focus inventory management effort?
3. Which products require a replenishment or excess-cover review under stated assumptions?
4. How do recent sales, zero-sale days, cancellations and exceptional orders affect those decisions?
5. What should management validate before changing a stock policy?

## First findings

Analysis period: **1 December 2010–30 November 2011**, twelve complete calendar months. Currency: **GBP**, without conversion to AUD.

| Measure | Result | Meaning |
| --- | ---: | --- |
| Gross merchandise sales | £9,655,544.63 | Positive, priced merchandise entries before cancellation/credit entries |
| Sales orders | 18,957 | Distinct invoices with an included positive sale |
| SKUs with sales | 3,789 | Merchandise code rule and positive-sale cohort |
| A-class SKUs | 825 | 21.8% of SKUs contribute 80.02% of gross sales |
| Highest revenue SKU | 22423 | Regency Cakestand 3 Tier; £168,477.87 gross sales |

**A finding that changes the recommendation:** SKU `23166` leads gross unit volume, but the source contains a 74,215-unit positive entry and an equal negative entry on 18 January 2011 at the same price. This is a candidate offset requiring investigation. It is not evidence of sustained demand or a confirmed linked return. Both entries remain visible.

See [findings and management actions](reports/findings.md), [credit review](reports/sku_credit_review.csv) and [same-day offset candidates](reports/same_day_offset_candidates.csv).

## Reproduce the analysis

Requires Python 3.11+ and an internet connection for the initial publisher download. Use a virtual environment, activate it for your operating system, then run:

```bash
git clone https://github.com/Jjamess413/inventory-sku-performance-analysis.git
cd inventory-sku-performance-analysis
python -m pip install -r requirements.txt
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/run_queries.py
```

The build downloads the original UCI archive, verifies its SHA-256 checksum, classifies transactions, creates a SQLite database, exports dashboard tables and writes reports. It does not require a Kaggle account or API key.

If downloading is unavailable, obtain the official workbook from the source page and save it as `data/raw/online_retail.xlsx`. The same checksum is required. A changed publisher file must be reviewed before updating the expected checksum.

Generated files:

- `data/processed/inventory.sqlite`: local SQL database with dimensions, transactions, analytical views and scenario tables.
- `data/processed/*.csv`: local Power BI inputs, generated from the full reviewed source.
- `data/synthetic/inventory_snapshot.csv`: deterministic, labelled scenario assumptions.
- `reports/*.csv` and `reports/*.json`: shareable aggregates, review queues and validation results.

Raw files, customer IDs and large transaction exports are excluded from Git. The public reports and source code allow the results to be checked without publishing the source workbook again.

## Repository guide

| Location | Purpose |
| --- | --- |
| [Data documentation](data/README.md) | Dataset comparison, provenance, licence and field lineage |
| [Cleaning decisions](docs/data_cleaning.md) | Exclusions, cancellations, duplicates and row reconciliation |
| [SQL](sql/) | Schema, analytical views and runnable business questions |
| [KPI definitions](docs/kpi_definitions.md) | Population, period, units, formula and limitations |
| [Power BI](powerbi/) | Model, Power Query starter, DAX and dashboard build instructions |
| [Findings](reports/findings.md) | Evidence, hypotheses, recommendations and success measures |
| [Learning exercises](docs/learning_exercises.md) | Small SQL tasks and interview discussion prompts |
| [Progress](docs/PROGRESS.md) | Completed work, owner tasks and next-session handover |
| [Portfolio roadmap](docs/PORTFOLIO_ROADMAP.md) | Milestones for the three projects |

## Method and validation

SQL covers filters, aggregation, `HAVING`, inner/left joins, `CASE`, CTEs, cumulative windows and `LAG`. A calendar join includes zero-sale days in demand estimates. ABC uses the full-period gross sales contribution; the threshold-crossing SKU remains in the higher-priority class.

The inventory module estimates safety stock and reorder points only for SKUs meeting a simple history and concentration screen. Other SKUs receive a manual review flag and a blank order recommendation. The screen is a teaching baseline, not a validated forecasting model.

The checked-in [validation report](reports/validation.json) records row reconciliation, referential integrity, monetary and volume reconciliation, ABC coverage, scenario labelling and eligibility checks. Hand-calculated tests check cleaning and business-rule edge cases.

## Important limits

- This is historical UK order data, including wholesale purchasing. Results do not describe the current Australian retail market.
- Gross sales are not profit, recognised accounting revenue or cash receipts. Credits are not matched to original sales, and 16 in-period credit rows for SKUs without positive sales are outside the model cohort.
- Exact repeats are retained because the data lacks an original unique invoice-line key. A deduplication sensitivity is reported.
- Actual stock, supplier deliveries, availability, lost sales, COGS and margins are unavailable. Actual stockout rate, financial inventory turnover and realised savings cannot be measured.
- Recent observed sales are a demand proxy. Unrecorded stockouts, closures, returns and product introductions can bias it. One year does not establish repeatable annual seasonality.
- The Power Query and DAX files are prepared for hands-on Desktop validation. No PBIX or Power BI dashboard screenshots have been produced yet.

## Source and attribution

Chen, D. (2015). **Online Retail** [Dataset]. UCI Machine Learning Repository. [DOI: 10.24432/C5BW33](https://doi.org/10.24432/C5BW33). [Source page](https://archive.ics.uci.edu/dataset/352/online+retail). Dataset licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Filtering, classification, aggregation and scenario additions are documented in this repository. See [data attribution](DATA_ATTRIBUTION.md).

Author: **James You**, Sydney. [LinkedIn](https://www.linkedin.com/in/zi-hao-you-1231112ab/).
