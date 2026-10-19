# Owner learning log

The first independently modified SQL submission and grouping explanation have been reviewed. The requested secondary SKU sort has now been observed in an owner-run query. Independent November filtering and HAVING explanation remain pending.

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

**Next learning step:** combine a November date filter with `HAVING SUM(quantity) >= 100`, then independently change the minimum to 5,000 and explain why the aggregate condition belongs in HAVING. The mentor reference query has been run: November has 2,889 SKUs with positive sales, of which 1,213 have at least 100 units. These reference results do not mark the owner's November exercise complete.

## Exercise review

| Topic | Owner explanation or query | Review status |
| --- | --- | --- |
| Top-ten volume ranking and `GROUP BY sku` explanation | Owner modification and explanation correct; secondary SKU sort observed in subsequent October query | Reviewed; requested correction verified |
| November SKU query: WHERE and HAVING | Guided October filter observed; November query and aggregate-filter explanation pending | Pending owner submission |
| Join grain and duplicate keys | Pending | Pending |
| ABC cumulative window | Pending | Pending |
| Zero-sale days and inventory assumptions | Pending | Pending |
| Power BI relationships and DAX | Pending | Pending |

Replace pending entries with James's actual work and the review outcome. Do not mark an item complete because a scaffold was generated.
