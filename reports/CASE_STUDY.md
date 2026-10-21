# Retail SKU prioritisation and stock review

**James You · Personal portfolio case study · October 2026**

## Decision problem

A retailer needs to focus product review effort, distinguish commercial demand from exceptional entries and decide what evidence to collect before replenishment decisions. Treating every product equally or treating gross volume as recurring demand can produce a poor review queue.

## Data and approach

The project uses UCI Online Retail orders from a UK-based retailer across all included countries. It analyses twelve complete months, 1 December 2010–30 November 2011, in GBP.

The reproducible pipeline reconciles 511,035 included transaction lines for 3,789 positive-sale SKUs. SQL separates sales and credits, preserves repeated rows with flags, computes ABC contribution using cumulative windows and includes zero-sale calendar days in the 90-day demand proxy. A distinct, deterministic scenario supplies assumed stock balances and supplier lead times.

## Findings

| Finding | Evidence | Proposed decision |
| --- | --- | --- |
| Concentrated sales contribution | 825 SKUs, 21.77% of the cohort, contribute 80.02% of £9,655,544.63 gross sales | Start a product-data and availability review with the commercial core; include margin and range purpose before final priorities |
| Revenue and units grew at different rates | November sales £1,457,742.24, up 31.72%; units 750,081, up 20.64% from 621,728 | Investigate product/price mix and order concentration; no causal price or seasonal claim is established |
| Exceptional volume needs investigation | SKU 23166 includes equal positive and negative 74,215-unit entries on one date; signed value is far below gross value | Ask sales operations and finance to inspect original order/credit records before using gross volume in replenishment |
| A transparent scenario creates review queues | 984 reorder-review, 509 excess-cover-review and 1,845 manual-review SKUs under stated synthetic assumptions | Validate observed inventory, supplier receipts and order constraints before a small monitored pilot |

## Deliverables

- Reproducible Python/SQLite pipeline, business queries and checked aggregate outputs.
- A working offline dashboard with sales filters, SKU search and a labelled scenario explorer.
- A native Power BI project with four tables, three relationships, 24 measures and three report pages. A Windows Desktop screenshot confirms executive overview refresh and four reconciled control totals; detailed page and interaction checks remain separately recorded.
- Validation evidence, data provenance, KPI definitions and documented limits.

## What this project demonstrates

The analytical contribution is a traceable prioritisation and investigation process: monitor sales, identify concentration and anomalies, explain the evidence boundary, then propose a review with measurable follow-up.

It does not demonstrate implemented savings, observed stockout reduction, profit improvement or financial inventory turnover. Costs, margins, observed inventory and service events are absent. The sales history includes wholesale purchasing and cannot establish repeatable annual seasonality from one cycle.

Suggested follow-up owners are inventory planning, purchasing, sales operations and finance. First measures should track data completeness and review resolution; operational service or financial improvements need observed baselines and an agreed intervention period.

Development was AI-assisted. James's guided SQL work and subsequent learning are recorded separately; postponed learning is not represented as completed independent authorship.
