# Learning exercises and interview preparation

These tasks are part of the project's completion criteria. Working starter code is available so development can progress while James practises. A scaffold or passing pipeline test is not evidence that the owner can independently explain it.

## Session 1: one row, one product and one total

**Why this matters:** a transaction table has many lines for the same product. Management asks for one total per product. `GROUP BY` changes the level of detail; `SUM` adds values within each group.

```sql
SELECT sku,
       SUM(quantity) AS units_sold,
       SUM(revenue_pence) / 100.0 AS gross_sales_gbp
FROM v_sales
GROUP BY sku
ORDER BY gross_sales_gbp DESC, sku
LIMIT 5;
```

Read it in business order: use included sales, group the lines by product, calculate units and value, then show the five highest values. `100.0` converts integer pence to pounds without integer division.

**Owner exercise:** change this query to November 2011 only and show products with at least 100 units sold during that month. Return the SQL and explain why the date condition belongs in `WHERE` and the quantity condition belongs in `HAVING`.

**Interview follow-up:** what changes if quantity rather than revenue determines the ranking? Why might one bulk order distort it?

## Session 2: joins without multiplying the answer

Use `INNER JOIN dim_sku` to add a product description to the first query. Reconcile its total with the query before the join. Explain why each SKU must occur once in the dimension.

Use a `LEFT JOIN` when checking whether a transaction's SKU is missing from the product dimension. Explain why an inner join would hide missing keys. The generated model should have none; that is a result to validate, not assume.

**Interview follow-up:** what happens to stock totals if a one-row-per-SKU snapshot is joined directly to many transaction rows?

## Session 3: ABC and window functions

Read the `sku_totals` and `running` CTEs in `sql/01_analysis_views.sql` separately. A CTE gives a useful name to a query step. The cumulative window calculates a running contribution without collapsing the individual product rows.

Hand-calculate ABC for four products contributing 60, 25, 10 and 5 currency units. Explain the threshold-crossing policy and the SKU tie-breaker. Then compare your answer with the hand-calculated SQL test.

**Interview follow-up:** why choose revenue-based ABC here? What would margin-based or inventory-value ABC require that this dataset lacks?

## Session 4: daily demand and a stock scenario

For daily sales `[3, 0, 0]`, calculate the average over three calendar days. Compare it with the average if only the day with sales is included. Then explain why a zero-sale day could also mean the item was unavailable.

With average demand 10 units/day, daily standard deviation 4 units, seven-day fixed lead time and z = 1.645, calculate the rounded safety stock and reorder point. Use the definitions in `docs/kpi_definitions.md`; do not interpret the answer as a guaranteed service level.

Explain inventory position for on-hand 100, on-order 30 and reserved 20. State what additional information is needed before placing a purchase order.

**Interview follow-up:** why are short history, intermittent sales and single-day concentration routed to manual review?

## Session 5: Power BI and DAX

Build the relationships and first two measures yourself, then use the prepared guide for the rest. Filter a SKU and a month. Explain filter context using the changing gross-sales measure.

Compare `SUM(revenue_pence)` with the independent `SUMX(quantity × unit_price_pence)` check. Explain stored line values, row context, measure aggregation and why a distinct invoice count differs from a line count.

Explain why historical date and country filters must not appear to recalculate the fixed global stock scenario.

## Git practice

- A repository stores the project and its change history.
- A commit records a meaningful version, with a message explaining the change.
- A branch separates work before it is brought into the main version.
- A README explains the business purpose, method, findings and how to run it.

Inspect `git status`, `git log --oneline` and `git diff` in a local clone. After completing an exercise, write your explanation in `docs/learning_log.md`, review its diff and commit that change. Use your existing GitHub sign-in workflow for publishing; do not put credentials in project files.

## Final independent walkthrough

Before publication as a completed project, James should be able to explain the business question, source and licence, row grain, cleaning choices, SQL joins and windows, KPI definitions, the 74,215-unit anomaly, dashboard interactions, synthetic assumptions and limitations without reading a generated script.

The 60-second and three-minute project pitches, resume bullets and LinkedIn Featured copy are release tasks after that walkthrough and the actual dashboard are complete.
