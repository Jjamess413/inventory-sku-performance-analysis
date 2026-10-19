# Owner learning log

One independently modified SQL submission has been reviewed. Core aggregation and ranking are correct; a small secondary-sort correction remains pending.

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

**Small correction requested:** retain `sku` as the secondary sort, giving `ORDER BY units_sold DESC, sku`. It makes tied-volume ordering explicit. The submitted ten rows have distinct volumes, so this omission does not alter the observed result; the requested correction has not yet been observed in an owner-run query.

**Next learning step:** add a date condition before aggregation, then introduce `HAVING` for a minimum monthly volume. The November exercise remains pending.

## Exercise review

| Topic | Owner explanation or query | Review status |
| --- | --- | --- |
| Top-ten volume ranking and `GROUP BY sku` explanation | Owner SQL and grouping explanation reviewed; all ten result rows match | Core logic correct; secondary SKU sort requested |
| November SKU query: WHERE and HAVING | Pending owner submission | Pending |
| Join grain and duplicate keys | Pending | Pending |
| ABC cumulative window | Pending | Pending |
| Zero-sale days and inventory assumptions | Pending | Pending |
| Power BI relationships and DAX | Pending | Pending |

Replace pending entries with James's actual work and the review outcome. Do not mark an item complete because a scaffold was generated.
