# Windows quick start

Use this guide to run the inventory project locally, inspect the results and begin the owner learning exercises.

**Environment confirmed:** James's first local Windows build passed all 14 pipeline checks on 19 October 2026, using Python 3.13.16 and pandas 3.0.6. The terminal output confirms 511,035 model rows and 3,789 model SKUs. Guided owner-run SQL queries and basic modifications have since been reviewed; see [the learning log](learning_log.md) for actual evidence and pending exercises. Windows unit tests, advanced exercises and Power BI Desktop validation remain separate milestones.

## 1. Prepare the tools

Skip software that is already installed.

| Tool | Purpose | Official source |
| --- | --- | --- |
| Python | Download and clean the UCI data; generate the SQLite database and report inputs | [Python for Windows](https://www.python.org/downloads/windows/) |
| DB Browser for SQLite | Open the generated database and run individual SQL queries | [DB Browser downloads](https://sqlitebrowser.org/dl/) |
| Power BI Desktop | Build and check the actual report in Windows | [Microsoft installation guide](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop) |

For a typical Intel or AMD Windows computer, choose the 64-bit installers. For an ARM computer, use the publishers' architecture-specific instructions.

Power BI Desktop is free to download. The Microsoft Store option supports automatic updates. Local report creation and saving a PBIX are the scope of this exercise; publishing and online sharing are a later step.

For a new Python installation, install the official **Python install manager** and reopen PowerShell. Install the standard Python 3.13 runtime:

```powershell
pymanager install 3.13
py -3.13 --version
```

If Python 3.11, 3.12 or 3.13 is already installed, keep that installation and use its version when creating the environment below, for example `py -3.12 -m venv .venv`. An older Python launcher may take priority for the `py` command and reject `py install`; use `pymanager install 3.13` to install the runtime, then verify it with `py -3.13 --version`. If `pymanager` is unavailable, reopen PowerShell after installing the official manager and check the publisher's troubleshooting guidance.

Initial project reference results were produced with Python 3.12.14 and pandas 2.2.3. The first owner-run Windows build also passed with Python 3.13.16 and pandas 3.0.6. A local build records its actual versions in `reports/validation.json`; the business-rule tests and Desktop checks must be verified separately.

## 2. Get the project

Open [the repository](https://github.com/Jjamess413/inventory-sku-performance-analysis), choose **Code > Download ZIP**, then extract it.

Use **Extract All** before opening the project: a File Explorer path containing `.zip` still refers to the archive. Open the extracted folder that contains `README.md`, `requirements.txt` and `scripts`.

Press **Alt+D** in File Explorer to select its address bar, type `powershell` and press Enter. Check that the new window's `PS ... >` prompt ends in the project folder. If it shows only a drive root, copy the extracted folder's full path from File Explorer and use `Set-Location -LiteralPath "YOUR_EXTRACTED_PROJECT_PATH"`, replacing the placeholder with that actual path. Keep quotes around paths containing spaces. Run `Get-ChildItem` to confirm that `requirements.txt` and `scripts` are present before creating `.venv`.

If you already have a local Git clone, use it instead. The ZIP route is enough for the first SQL exercise. Git version-control practice follows in [learning exercises](learning_exercises.md#git-practice).

**The generated SQLite database and dashboard CSV inputs are not included in the download.** The build creates them locally from the original UCI source.

## 3. Build and validate

Run **one line at a time**. Continue only when the previous command completes successfully.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\build.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\run_queries.py
```

Use the Python version selected in step 1 for the first line. All later lines use the project's environment directly, so a separate activation step is unnecessary.

The first build downloads the original UCI archive and checks the reviewed source checksum. Allow the command to finish before running the next one. Close DB Browser's database connection and any file previews before rebuilding on Windows, because open handles may prevent replacement of the finished database.

Expected successful checks:

- The build prints `"status": "PASS"`, with 14 checks, 511,035 model rows and 3,789 model SKUs.
- Unit tests report `Ran 10 tests` and `OK`.
- The saved-query runner completes and writes `reports/query_validation.json` with `"passed": true` and `"queries_executed": 11`.

The first Windows build's 14 pipeline checks have been observed in James's terminal screenshot. The Windows unit-test and saved-query results have not yet been reviewed; the expectations above do not mark those tasks complete.

If a command fails, stop and share the command and error text. Keep the source checksum check in place. If the publisher download is unavailable, the main README describes the official-workbook fallback.

## 4. Run the first SQL query yourself

1. Open **DB Browser for SQLite**.
2. Choose **Open Database** and select `data\processed\inventory.sqlite` inside the extracted project.
3. Select **Execute SQL**.
4. Paste this query and run it using the execute button:

```sql
SELECT
    sku,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue_pence) / 100.0, 2) AS gross_sales_gbp
FROM v_sales
GROUP BY sku
ORDER BY gross_sales_gbp DESC, sku
LIMIT 5;
```

Business question: **Which five products generated the highest gross merchandise sales during the selected twelve complete months?**

| SQL part | Business meaning |
| --- | --- |
| `FROM v_sales` | Use included positive sales for 1 December 2010 to 30 November 2011 |
| `GROUP BY sku` | Return one row for each product, rather than one row per transaction line |
| `SUM(quantity)` | Add the units sold for each product |
| `SUM(revenue_pence) / 100.0` | Add line values held in pence and convert the result to GBP |
| `ORDER BY ... DESC, sku` | Put highest sales first, with SKU as a deterministic tie-breaker |
| `LIMIT 5` | Show five products |

The result is gross sales **before cancellation/credit entries**. It is not profit. The source is historical UK retail data, not employer data.

Reference results checked against the existing validated project database:

| sku | units_sold | gross_sales_gbp |
| --- | ---: | ---: |
| 22423 | 13,429 | 168,477.87 |
| 85123A | 37,113 | 104,085.75 |
| 47566 | 18,159 | 98,585.85 |
| 85099B | 47,369 | 92,113.15 |
| 23166 | 77,826 | 81,448.21 |

SKU `23166` includes the documented exceptional 74,215-unit positive entry. The gross-sales view deliberately keeps it visible. The equal negative entry is reviewed separately; neither establishes normal replenishment demand.

**First small exercise:** change the query to show ten products and explain, in your own words, why `GROUP BY sku` is needed. Send the SQL and explanation for review.

Then attempt the November-only exercise in [Session 1](learning_exercises.md#session-1-one-row-one-product-and-one-total). Write your own work and review outcome in [the learning log](learning_log.md). Prepared reference code does not count as an independently completed exercise.

**Interview connection:** be ready to explain the row grain before and after aggregation, why revenue and units can produce different rankings, and why a gross-sales ranking alone is insufficient for a replenishment decision.

## 5. Continue to Power BI

After the local build and first SQL exercise succeed, follow [the Power BI Desktop build guide](../powerbi/README.md).

The build generates these four model inputs in `data\processed\`:

- `fact_transactions.csv`
- `dim_sku.csv`
- `dim_date.csv`
- `inventory_scenario.csv`

Use the prepared Power Query queries to preserve identifier types and validate columns. The guide explains the `pDataFolder` parameter, relationships, DAX measures and page layouts.

Reconcile the first page against gross merchandise sales of **GBP 9,655,544.63**, **18,957** sales orders and **3,789** active SKUs. Keep every inventory visual labelled as a synthetic scenario. Actual Desktop execution, interactions, PBIX and screenshots remain pending until checked on Windows.

## Official references

- [Using Python on Windows](https://docs.python.org/3/using/windows.html)
- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [DB Browser for SQLite downloads](https://sqlitebrowser.org/dl/)
- [Download Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop)
