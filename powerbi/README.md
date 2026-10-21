# Power BI Desktop build guide

**Current delivery:** a native [InventoryPortfolio.pbip](InventoryPortfolio.pbip) project with four import tables, three single-direction relationships, 24 measures and three report pages. Public JSON schema and field-reference checks pass. An owner-provided Windows Desktop screenshot confirms the refreshed executive overview and all four control totals. Other native page and slicer checks remain listed in the [Desktop evidence record](../reports/powerbi_desktop_validation.json).

## Open the ready project

Follow [START_HERE.md](../START_HERE.md). The portable package already supplies the local CSV inputs. Double-click `OPEN_POWERBI.cmd` at the root, then click **Refresh** in Desktop. The launcher configures the data-folder parameter from the extracted folder; the pages, relationships and measures are already present.

For a fresh Git clone, run `scripts/build.py`, `scripts/build_dashboard.py` and `scripts/build_powerbi.py` first. Full transaction CSVs and the database are deliberately excluded from Git.

The semantic model uses supported TMSL `model.bim` and the report uses PBIR. [all_measures.dax](all_measures.dax) mirrors the authored model. [Source validation](../reports/powerbi_source_validation.json) documents what has been checked; it does not claim Desktop execution.

The corrected 21 October package aligns the report shell with Microsoft report-authoring CLI 0.5.0: `definition.pbir` binding version 4.0, PBIR content version 2.0.0, report platform metadata, and a registered base-theme resource. Its [offline CLI validation](../reports/powerbi_cli_validation.json) reports zero diagnostics. The corrected project was reopened and refreshed successfully; the [executive overview capture](screenshots/powerbi-executive-overview.png) records the result.

The included `Fluent2-CY26SU10.json` base theme comes from the official CLI scaffold. Microsoft's MIT [licence](MICROSOFT_LICENSE) and [notice](MICROSOFT_NOTICE) are retained. Reference: [Microsoft PBIR authoring scaffold documentation](https://github.com/microsoft/skills-for-fabric/blob/main/skills/powerbi-report-cli/references/authoring-part-02.md).

The remaining sections are a manual construction/reference guide, not required hand-authoring steps for the delivered PBIP.

## 1. Generate the inputs

Run `python scripts/build.py` followed by `python scripts/build_dashboard.py`. Local inputs are in `data/processed/`:

- `fact_transactions.csv`
- `dim_sku_portfolio.csv` (the extended product dimension with fixed ABC, revenue rank and display label)
- `dim_date.csv`
- `inventory_scenario.csv`
- `demand_stats.csv` (optional diagnostic table; not required in the report model)

## 2. Load and inspect with Power Query

1. Open Power BI Desktop on a supported Windows environment and create a blank report.
2. Select **Transform data**. In **Manage Parameters**, create a text parameter named `pDataFolder` containing your full `data/processed/` folder path, including its trailing path separator.
3. Create a blank query named `fxLoadCsv`. Paste [fxLoadCsv.pq](powerquery/fxLoadCsv.pq) into its Advanced Editor.
4. Create separate blank queries named `FactTransactions`, `DimSKU`, `DimDate` and `InventoryScenario`. Paste the corresponding `.pq` file into each query. Each file is one query, not one combined script.
5. Inspect identifiers as text, quantities and money in pence as whole numbers, and dates as Date. Check that cancellation quantities remain negative. The starter deliberately raises an error for broken keys or unexpected values.
6. In Power Query, inspect column quality and compare row counts with the control totals below. Explain why deleting missing-customer rows or duplicate product keys would change the result.
7. Close & Apply. Disable load for `fxLoadCsv` if applicable. Do not import the source CustomerID field.

The source cleaning decisions are implemented in the reproducible pipeline. These Power Query steps handle CSV parsing, schema/type validation and identifier normalisation without silently changing the analysis population.

## 3. Create the relationships

| One side | Many side | Direction | Purpose |
| --- | --- | --- | --- |
| DimSKU[sku] | FactTransactions[sku] | Single, dimension to fact | Sales by product |
| DimDate[date] | FactTransactions[date] | Single, dimension to fact | Historical sales trends |
| DimSKU[sku] | InventoryScenario[sku] | Single, dimension to fact | Scenario by product |

`InventoryScenario` currently has one row per SKU at one snapshot. Configure the relationship as one-to-many with DimSKU on the one side, even if Desktop initially suggests one-to-one. Avoid the bidirectional filtering implied by a one-to-one default.

Do **not** join FactTransactions directly to InventoryScenario or connect the historical date dimension to the single snapshot. A transaction-to-snapshot join would multiply stock quantities by the number of sales rows.

Mark DimDate as the date table using its date column. Sort month labels by an appropriate date/month key. `month` is ISO year-month text and already sorts chronologically. Keep the model small and use explicit measures.

## 4. Add measures

The delivered PBIP already contains the measures. For manual recreation, [all_measures.dax](all_measures.dax) lists all definitions; [measures.dax](measures.dax) retains the earlier starter set. A DAX file with multiple definitions cannot be pasted into one measure editor.

Format GBP measures as pounds sterling, quantities as whole numbers, and percentages as percentages. Keep the scenario label visible beside every stock visual. The independent SUMX check should match the stored line-value sum.

## 5. Build three report pages

| Page | Visuals | Filters and definitions |
| --- | --- | --- |
| Executive Overview | Cards for gross sales, gross units, orders and SKUs; monthly sales line; top-ten SKU revenue bars; ABC sales-share bars | Historical date and country slicers. Show GBP and the selected date range. ABC labels stay fixed to the original full-period all-country classification. |
| SKU & Inventory Performance | SKU table with gross sales, units, ABC and scenario status; quantity/revenue ranking; demand eligibility breakdown | SKU and ABC slicers. Separate historical metrics from the fixed snapshot. A country filter applies to sales only, not global scenario stock. |
| Stock Optimisation & Recommendations | Cards for scenario reorder review, excess-cover review and manual review; table of assumptions, ROP and suggested order; short management actions | SKU and ABC filters only. State: “Synthetic stock scenario as at 30 November 2011; fixed 90-day sales lookback.” Do not add date or country slicers suggesting policy recalculation. |

Use a restrained navy/teal palette, legible titles and whitespace. Use amber for review and keep actual sales and hypothetical stock visually distinct. Put assumptions in ordinary readable notes, not hidden tooltips alone.

## 6. Reconcile before exporting

With no filters applied:

| Check | Expected |
| --- | ---: |
| FactTransactions rows | 511,035 |
| DimSKU rows | 3,789 |
| DimDate rows | 365 |
| InventoryScenario rows | 3,789 |
| Gross Merchandise Sales GBP | 9,655,544.63 |
| Gross Units | 5,263,714 |
| Sales Orders | 18,957 |
| Active SKUs | 3,789 |
| Cancellation Value GBP | 304,386.95 |
| Gross Sales Calculation Difference GBP | 0.00 |

Check a SKU, a month, a cancellation and a manual-review product. A manual-review item must show a blank suggested order rather than an apparently valid zero. Compare scenario counts with `reports/scenario_summary.csv` after every pipeline change.

Test slicers, cross-highlighting, page navigation and resetting filters. Confirm date and country changes do not alter the fixed inventory scenario. These are Desktop checks, not validations already completed by the Python tests.

## 7. Save and capture

Save a local PBIX once totals and interactions pass. Export one readable screenshot per page into `powerbi/screenshots/`. Retain the source code and model documentation alongside screenshots. The repository currently ignores PBIX files so a file is not published accidentally before its contents are reviewed.

Record native acceptance after the actual Desktop project refresh, control totals and interactions pass and actual Desktop captures are available. Owner learning/explanation is tracked separately and has been deferred by explicit request on 21 October 2026. Browser screenshots must remain labelled as browser screenshots.

Reference: [Microsoft Power BI star-schema guidance](https://learn.microsoft.com/power-bi/guidance/star-schema), [relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand), [measures](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures), [SUMX](https://learn.microsoft.com/dax/sumx-function-dax).
