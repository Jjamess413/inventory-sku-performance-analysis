# Owner learning log

The original entries below preserve the learning sequence. Subsequent guided CTE, cumulative ABC and monthly-growth work was reviewed in the 19–20 October conversation. James requested delivery first on 21 October and deferred further learning. No independent-from-scratch authorship or unobserved Desktop work is inferred from generated code. See the latest dated entry at the end of this file.

## Guided execution observed: 19 October 2026

James opened the generated local database in DB Browser for SQLite and executed the supplied revenue-ranking query. His result screenshot shows five rows, no execution error and a match with the reference values:

| SKU | Units sold | Gross sales GBP |
| --- | ---: | ---: |
| 22423 | 13,429 | 168,477.87 |
| 85123A | 37,113 | 104,085.75 |
| 47566 | 18,159 | 98,585.85 |
| 85099B | 47,369 | 92,113.15 |
| 23166 | 77,826 | 81,448.21 |

This verifies execution of prepared SQL, not independent authorship or understanding. Gross sales are before cancellation/credit entries. SKU 23166 retains the documented exceptional positive entry and requires investigation before interpreting its gross volume as replenishment demand.

## Exercise 1 submission: 19 October 2026

James changed the prepared query's primary sort to `units_sold DESC` and its limit to ten rows. All ten submitted result rows match an independent read-only execution against the validated project database.

Owner-submitted SQL, transcribed from the result screenshot:

```sql
SELECT
    sku,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue_pence) / 100.0, 2) AS gross_sales_gbp
FROM v_sales
GROUP BY sku
ORDER BY units_sold DESC
LIMIT 10;
```

Owner explanation, translated from Chinese: "Group by SKU combines all sales records for the same SKU."

**Review:** the grouping explanation, descending volume ranking and ten-row limit are correct. More precisely, `GROUP BY` forms one group per SKU within `v_sales`, while `SUM` calculates the totals for each group. This query returns one row per SKU and leaves the underlying transaction records unchanged.

**Correction verified:** the owner's subsequent October query includes `ORDER BY units_sold DESC, sku`. All ten result rows match an independent read-only query. SKUs 21915 and 22178 both have 3,320 units and appear in ascending SKU order, demonstrating the tie-breaker on an actual tie. The original submission above remains unchanged as a record of the first attempt.

**Guided date filter observed:** the owner executed the supplied October example with `WHERE date >= '2011-10-01' AND date < '2011-11-01'` before `GROUP BY`. The top SKU is 84077 with 8,180 units. The owner asked about TEXT date storage and comparisons, then reported understanding the explanation; an independent explanation has not yet been reviewed.

## Exercise 2 review: November WHERE and HAVING

James modified the supplied November query's minimum monthly quantity to 5,000 and provided a successful result screenshot. The date bounds, grouping, aggregate filter and secondary SKU sort are correct. All seven rows match an independent read-only execution.

Owner-executed SQL, modified from the mentor scaffold:

```sql
SELECT
    sku,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue_pence) / 100.0, 2) AS gross_sales_gbp
FROM v_sales
WHERE date >= '2011-11-01'
  AND date < '2011-12-01'
GROUP BY sku
HAVING SUM(quantity) >= 5000
ORDER BY units_sold DESC, sku;
```

| SKU | November units | Gross sales GBP |
| --- | ---: | ---: |
| 23084 | 14,954 | 34,556.72 |
| 22197 | 12,460 | 14,195.60 |
| 22086 | 7,908 | 28,985.04 |
| 85099B | 5,909 | 11,641.37 |
| 22578 | 5,366 | 1,787.50 |
| 84879 | 5,254 | 8,440.94 |
| 22577 | 5,003 | 1,658.29 |

Owner explanation, translated from Chinese: "Quantity is the number for an individual sales activity."

**Review:** this correctly identifies the line-level nature of quantity. More precisely, it is the quantity on one transaction line; one invoice can contain multiple lines. WHERE filters the input transaction lines, while HAVING filters the monthly SKU totals after grouping.

The owner initially reported 1,213 rows, which corresponds to the 100-unit reference. After changing the threshold and rerunning, the screenshot confirms seven rows for 5,000 units. Basic row-versus-group filtering is reviewed at this level; this is not evidence of writing the whole query without a scaffold.

**Product-lookup reference:** the mentor checked the INNER JOIN example against the database: the same seven SKUs, quantities and sales values are retained; product keys are unique and sales keys have no missing product matches. Owner execution is reviewed below; independent join-grain explanation remains pending.

## Exercise 3 review: product lookup and column alias

James executed the supplied INNER JOIN query and independently changed the displayed product-name column to `p.description AS product_name`. His screenshot shows seven rows with product names and the same SKU quantities and sales values as the pre-join November result.

Owner-executed SQL, modified from the mentor scaffold:

```sql
SELECT
    s.sku,
    p.description AS product_name,
    SUM(s.quantity) AS units_sold,
    ROUND(SUM(s.revenue_pence) / 100.0, 2) AS gross_sales_gbp
FROM v_sales AS s
INNER JOIN dim_sku AS p
    ON s.sku = p.sku
WHERE s.date >= '2011-11-01'
  AND s.date < '2011-12-01'
GROUP BY s.sku, p.description
HAVING SUM(s.quantity) >= 5000
ORDER BY units_sold DESC, s.sku;
```

**Review:** the column alias is correct and is visible as `product_name` in the returned results. The grouping continues to use the source field `p.description`. SKU 23084 has the description RABBIT NIGHT LIGHT, 14,954 units and GBP 34,556.72 in gross sales. All seven product names and metric values match the mentor's previously verified reference.

This verifies guided JOIN execution and the owner's column-alias modification. The duplicate-match thought exercise is reviewed below; a fuller independent explanation of matching keys and row preservation remains pending.

**Join-validation follow-up:** James correctly answered the teaching scenario: two matching product rows produce two joined rows for one 10-unit sales line, giving a summed quantity of 20. This is a hypothetical example, not an observed duplicate in the project data. The mentor's duplicate-key check returns no duplicates; James's execution result for that separate check has not been supplied.

James reports zero rows for the supplied LEFT JOIN missing-product check, consistent with the mentor's existing validation. This is recorded as an owner-reported result; a new query screenshot was not supplied. He initially described LEFT JOIN as preserving columns. Feedback clarified that it preserves left-side rows at the join step, that SELECT chooses the output columns, and that a later WHERE condition can filter the joined rows. An independent restatement of that correction remains pending.

## Exercise 4 review: CASE WHEN threshold change

The mentor's teaching example bands November sales by monthly units: at least 10,000 is High volume, at least 5,000 is Medium volume, and otherwise Lower volume, evaluated in that order. These illustrative labels are separate from the project's revenue-based ABC policy and do not establish an inventory recommendation.

James reports that changing the first threshold to 7,000 changes SKU 22086 to High volume, explaining that its volume is 7,908. This matches the mentor's independently executed reference. A new owner query or screenshot was not supplied, so execution is recorded as owner-reported and the threshold explanation is reviewed as correct. Independent explanation of first-matching-condition behaviour remains to be revisited.

Across all 2,889 November sales SKUs, the mentor reference has 2 high, 5 medium and 2,882 lower at the 10,000-unit threshold; the 7,000-unit variant has 3 high, 4 medium and 2,882 lower.

**Next learning step: a named CTE result.** The mentor has executed a two-stage `monthly_sales` example: aggregate November transactions to one row per SKU, then filter the resulting `units_sold` rows in an outer WHERE. At a minimum of 5,000 units it reproduces the same seven SKU quantities as the earlier HAVING query. The CTE is a named query result scoped to the statement, not a permanent table.

Owner exercise: calculate `gross_sales_gbp` inside the CTE and include that column in the outer SELECT, keeping the seven-row cohort. The mentor reference for this extension has been executed; owner SQL and explanation remain pending.

## Exercise review

| Topic | Owner explanation or query | Review status |
| --- | --- | --- |
| Top-ten volume ranking and `GROUP BY sku` explanation | Owner modification and explanation correct; secondary SKU sort observed in subsequent October query | Reviewed; requested correction verified |
| November SKU query: WHERE and HAVING | Modified mentor scaffold; seven rows verified at a 5,000-unit threshold; line-level quantity explanation reviewed | Reviewed at basic exercise level |
| Product-lookup INNER JOIN and column alias | Seven named SKU rows reconcile; owner applied `AS product_name` correctly | Execution and modification reviewed |
| Join grain and duplicate/missing keys | Duplicate-match scenario correct; owner reports zero missing matches; duplicate-count output and corrected row-preservation explanation pending | Partly reviewed |
| CASE WHEN volume bands | Owner reports SKU 22086 becomes High volume at 7,000 units because it sold 7,908; matches reference | Threshold reasoning reviewed; condition-order explanation to revisit |
| CTE monthly-sales result | Guided monetary extension and later monthly comparisons reviewed in the subsequent conversation | Guided work reviewed; independent explanation to continue |
| ABC cumulative window | November class counts, share formulas and combined five-column output reviewed in owner screenshots | Guided work reviewed; boundary policy clarified below |
| Zero-sale days and inventory assumptions | Pending | Pending |
| Power BI relationships and DAX | Pending | Pending |

Replace pending entries with James's actual work and the review outcome. Do not mark an item complete because a scaffold was generated.

## Subsequent guided work and delivery priority: 21 October 2026

The visible 19–20 October continuation contains the following reviewed work:

- The owner correctly predicted that LIMIT does not change the earlier window total; reported 2.37% for the leading November SKU and 11.31% cumulative share for the top ten.
- The owner initially reversed ABC interpretation, accepted the correction, then supplied the successful November five-column summary: A 615, B 725, C 1,549; sales shares 79.98%, 15.02%, 5.01%. The screenshot amounts sum to £1,457,742.24 and the counts to 2,889.
- The owner corrected an extra aggregation layer in the SKU-share expression after feedback; the combined result screenshot shows the corrected expressions.
- The owner supplied October sales £1,106,666.53 and explained November's 31.72% month-on-month growth correctly.
- The owner correctly identified that October has no earlier row within the filtered LAG input and placed the November-only display filter outside the comparison CTE.
- The quantity extension included SUM(quantity) and LAG(units_sold); passing units_sold through the second CTE and adapting the growth expression still required guidance. The delivery pipeline's 20.64% quantity growth is analyst-verified, not an owner-reported independent answer.

**ABC scope/boundary clarification:** the November exercise classified the current item's end cumulative share at <=80/<=95. The released model uses twelve complete months and retains the threshold-crossing item in the higher-priority class, based on the cumulative share before that item. Its 825/963/2,001 counts are deliberately different in both scope and boundary policy. Browser and native report filters keep this full-period classification fixed.

**Owner priority:** complete the project today; learning can follow. Further quizzes, independent walkthroughs and lessons are therefore postponed rather than used as a delivery gate. The source implementation remains openly AI-assisted. Native Windows execution is still an actual acceptance requirement and has not been invented.
