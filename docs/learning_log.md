# Owner learning log

No independently modified SQL exercises have been reviewed yet.

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

## Exercise review

| Topic | Owner explanation or query | Review status |
| --- | --- | --- |
| Top-ten volume ranking and `GROUP BY sku` explanation | Pending owner submission | Pending |
| November SKU query: WHERE and HAVING | Pending owner submission | Pending |
| Join grain and duplicate keys | Pending | Pending |
| ABC cumulative window | Pending | Pending |
| Zero-sale days and inventory assumptions | Pending | Pending |
| Power BI relationships and DAX | Pending | Pending |

Replace pending entries with James's actual work and the review outcome. Do not mark an item complete because a scaffold was generated.
