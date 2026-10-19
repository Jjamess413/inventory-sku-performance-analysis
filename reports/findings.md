# Findings and proposed management actions

Analysis: included UK merchandise orders, 1 December 2010–30 November 2011. Currency: GBP. These are historical observations and hypothetical recommendations, not realised improvements at an employer.

## 1. Prioritise the commercial core

**Observed:** 825 of 3,789 SKUs (21.8%) contribute £7,726,096.26, or 80.02% of gross merchandise sales. A further 963 B-class SKUs contribute 14.99%; 2,001 C-class SKUs contribute 5.00%.

**Implication:** management can concentrate its initial replenishment and product-data review on a much smaller group. Revenue-based ABC does not establish product profitability, strategic importance or actual shortage risk.

**Proposed action:** start an inventory review with the top 20 A-class SKUs. Obtain observed balances, supplier receipts, current lead times and availability data before changing orders. Review C-class products for range purpose, margin and substitution before considering removal.

Evidence: [ABC summary](abc_summary.csv), [top revenue SKUs](top_revenue_skus.csv).

## 2. Investigate the volume leader before using it as a demand signal

**Observed:** SKU `23166` has 77,826 positive sale units and 74,494 credited units during the reporting period. Its gross sales are £81,448.21; its signed transaction value is £3,968.57. The source contains equal-and-opposite entries of 74,215 units on 18 January 2011 at £1.04 per unit.

**Supported conclusion:** gross-unit ranking is heavily affected by an exceptional entry. A same-day price/quantity match is an offset candidate. The available analysis does not prove which invoices belong together, whether a physical shipment occurred or why the entries were recorded.

**Hypotheses to validate:** order-entry correction, cancellation of a wholesale order, or a return/credit process. The model does not select one of these as a confirmed root cause.

**Proposed action:** review the original order and credit records with the sales/finance team. Maintain separate gross sales and credit views and compare commercial priorities using signed values. Do not convert the exceptional gross volume directly into a purchase order.

Evidence: [SKU credit review](sku_credit_review.csv), [same-day offset candidates](same_day_offset_candidates.csv). Both signs remain in the model.

## 3. Plan for the observed late-period rise, then validate the cause

**Observed:** November 2011 gross merchandise sales are £1,457,742.24, 31.72% above October's £1,106,666.53. November is the highest complete month in this window.

**Hypotheses:** holiday demand, wholesale orders and product mix may contribute. One observed annual cycle does not establish a repeatable seasonal pattern or prove the cause of the rise.

**Proposed action:** review SKU-level weekly demand and order concentration with merchandising before the next comparable period. Compare a second annual cycle if available, then test replenishment assumptions against held-out observations and actual availability.

Evidence: [monthly sales](monthly_sales.csv). The final partial December in the source is excluded from the monthly comparison.

## 4. Use the stock scenario as a review queue

**Synthetic scenario only:** 984 SKUs receive a reorder-review flag, 509 an excess-cover-review flag, 451 are within the illustrative policy, and 1,845 require manual demand review. Of the reorder-review group, 346 are A-class products.

These counts are generated from assumed stock and lead times. They are not observed shortages, overstock or measured retailer performance. They change when scenario assumptions change.

**Method observation:** 92 SKUs are withheld specifically for single-day concentration after the other history screens. In total, only 1,944 SKUs pass the baseline eligibility screen. That screen does not prove a suitable normal-demand distribution; the remaining products need a more appropriate method or operational investigation.

**Proposed action:** test a small, reviewed pilot with observed inventory and supplier data. Show the reason a product entered each queue. Keep automatic quantities blank for manual-review items.

Evidence: [scenario summary](scenario_summary.csv), [demand eligibility](demand_eligibility.csv), [review queue](scenario_review_queue.csv).

## Proposed follow-up plan

| Action | Proposed owner | Evidence required | Measure of progress |
| --- | --- | --- | --- |
| Resolve exceptional sale/credit candidates | Sales operations and finance | Linked order and credit records | Number reviewed, classification and unresolved value |
| Pilot A-class inventory review | Inventory planner | Observed stock, receipts, availability and supplier lead times | Data completeness and review completion; then monitored active-SKU stockout days |
| Validate lead-time assumptions | Purchasing | Purchase-order and receipt timestamps | Lead-time distribution and the share within the planning assumption |
| Review high cover and slow-moving range | Merchandising and finance | On-hand value, unit cost, margin, lifecycle and substitution | Products reviewed and approved decisions; subsequent observed cover and aged stock |
| Assess replenishment baseline | Analyst and inventory planner | Held-out demand proxy plus observed availability | Forecast error/bias and service outcomes under an agreed test design |

Record a baseline and observation period before claiming an improvement. Cost reduction, working-capital release, stockout reduction and profit improvement have not been measured or implemented by this project.
