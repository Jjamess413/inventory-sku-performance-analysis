# Standalone interactive dashboard

Open [index.html](index.html) locally after downloading the repository ZIP. There is no server, account, JavaScript dependency or external runtime request.

| Page | Working features |
| --- | --- |
| Executive overview | Month/country filters, reconciled KPIs, twelve-month trend, ABC contribution, top-ten products and management review notes |
| SKU explorer | Search, ABC filter, revenue/units/credit sorting, pagination and filtered CSV export |
| Stock review scenario | Fixed synthetic snapshot, class/status/search filters, product assumption details and review-queue export |
| Method & evidence | Provenance, definitions, assumptions, reproducibility and separate native Power BI delivery status |

The embedded data contains 62,679 SKU × month × country aggregates plus a 3,789-SKU catalogue and a labelled synthetic snapshot. There are no original invoice lines or customer IDs in the HTML. Order counts are aggregated separately; the build verifies that each included invoice belongs to exactly one month/country cell before summing those cells.

Historical filters apply to the overview and SKU explorer. Scenario controls use only the product/class/status fields: historical filters never change stored stock assumptions. ABC remains the full-period classification; it is not recomputed by the date/country controls.

The browser top-ten ranking recalculates for the selected sales context. The native Power BI overview intentionally displays selected-period sales for the **fixed full-period top ten**, as stated in its chart title.

## Actual browser captures

- [Executive overview](screenshots/browser-overview.png)
- [SKU explorer](screenshots/browser-sku-explorer.png)
- [Synthetic stock review](screenshots/browser-stock-scenario.png)

These are captures of the running HTML report, **not Power BI Desktop screenshots**.

## Rebuild and verify

```bash
python scripts/build_dashboard.py
# Optional browser developer test, after installing Playwright and Chromium:
node scripts/verify_dashboard.cjs
```

Fifteen runtime checks cover independent SQL reconciliation, country/month filtering, fixed scenario scope, blank manual-review quantities, search, sorting, pagination, details, CSV export, mobile width and JavaScript/network errors. See [runtime validation](../reports/dashboard_runtime_validation.json).
