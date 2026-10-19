# Owner learning log

The owner's initial aggregation/ranking exercise and modified November WHERE/HAVING query have been reviewed. The requested secondary SKU sort is verified. Basic row-versus-group filtering has been explained; JOIN practice, later analytical concepts and Desktop validation remain pending.

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

**Next learning step:** use an INNER JOIN to attach the product description from `dim_sku`. The mentor has checked the example against the database: the same seven SKUs, quantities and sales values are retained; product keys are unique and sales keys have no missing product matches. Owner-run JOIN output and an explanation are still pending.

## Exercise review

| Topic | Owner explanation or query | Review status |
| --- | --- | --- |
| Top-ten volume ranking and `GROUP BY sku` explanation | Owner modification and explanation correct; secondary SKU sort observed in subsequent October query | Reviewed; requested correction verified |
| November SKU query: WHERE and HAVING | Modified mentor scaffold; seven rows verified at a 5,000-unit threshold; line-level quantity explanation reviewed | Reviewed at basic exercise level |
| Join grain and duplicate keys | Mentor lookup example validated; owner execution and explanation pending | Pending |
| ABC cumulative window | Pending | Pending |
| Zero-sale days and inventory assumptions | Pending | Pending |
| Power BI relationships and DAX | Pending | Pending |

Replace pending entries with James's actual work and the review outcome. Do not mark an item complete because a scaffold was generated.
