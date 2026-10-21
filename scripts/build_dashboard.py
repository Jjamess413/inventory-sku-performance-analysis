"""Build the standalone portfolio dashboard from the validated SQLite model.

No service, credentials, customer IDs or JavaScript dependencies are required.
The HTML contains monthly/SKU/country aggregates, never original invoice lines.
"""
from pathlib import Path
import csv
import hashlib
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[1]


def rows(db, sql):
    return [dict(row) for row in db.execute(sql)]


def save_csv(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)


def build():
    db_path = ROOT / "data/processed/inventory.sqlite"
    if not db_path.exists():
        raise SystemExit("Run python scripts/build.py first.")
    db = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    validation = json.loads((ROOT / "reports/validation.json").read_text())
    if validation.get("passed") is not True:
        raise ValueError("The source analysis must pass validation before publication.")

    catalog = rows(db, """SELECT d.sku,d.description,d.first_sale_date,d.last_sale_date,
        a.abc_class,a.revenue_rank,d.sku || ' | ' || d.description AS product_label
        FROM dim_sku d JOIN sku_abc a ON d.sku=a.sku ORDER BY a.revenue_rank""")
    save_csv(ROOT / "data/processed/dim_sku_portfolio.csv", catalog)
    lookup = {item["sku"]: i for i, item in enumerate(catalog)}
    countries = [row[0] for row in db.execute("SELECT DISTINCT country FROM fact_transactions ORDER BY country")]
    country_lookup = {country: i for i, country in enumerate(countries)}
    months = [row[0] for row in db.execute("SELECT DISTINCT month FROM dim_date ORDER BY month")]
    month_lookup = {month: i for i, month in enumerate(months)}
    grouped = rows(db, """SELECT sku,SUBSTR(date,1,7) AS month,country,
        SUM(CASE WHEN transaction_type='sale' THEN quantity ELSE 0 END) AS units,
        SUM(CASE WHEN transaction_type='sale' THEN revenue_pence ELSE 0 END) AS sales_pence,
        -SUM(CASE WHEN transaction_type='cancellation' THEN revenue_pence ELSE 0 END) AS credit_pence,
        -SUM(CASE WHEN transaction_type='cancellation' THEN quantity ELSE 0 END) AS credit_units
        FROM fact_transactions GROUP BY sku,SUBSTR(date,1,7),country ORDER BY 1,2,3""")
    aggregated = [[lookup[r["sku"]], month_lookup[r["month"]], country_lookup[r["country"]],
                   r["units"], r["sales_pence"], r["credit_pence"], r["credit_units"]] for r in grouped]

    # Orders can only be summed across month/country if an invoice belongs to
    # exactly one such cell. Validate that fact instead of silently double-counting.
    invoice_conflicts = db.execute("""SELECT COUNT(*) FROM (
        SELECT invoice_no FROM v_sales GROUP BY invoice_no
        HAVING COUNT(DISTINCT country || '|' || SUBSTR(date,1,7)) > 1)""").fetchone()[0]
    if invoice_conflicts:
        raise ValueError("Order aggregation grain changed; review invoice logic.")
    orders = [[month_lookup[r["month"]], country_lookup[r["country"]], r["orders"]]
              for r in rows(db, """SELECT SUBSTR(date,1,7) AS month,country,
                  COUNT(DISTINCT invoice_no) AS orders FROM v_sales GROUP BY 1,2 ORDER BY 1,2""")]
    policy = rows(db, """SELECT sku,scenario_flag,demand_status,on_hand_units,on_order_units,
        reserved_units,lead_time_days,inventory_position_units,mean_daily_units,std_daily_units,
        safety_stock_units,reorder_point_units,target_stock_units,suggested_order_units,days_cover,
        observation_days,active_sales_days,largest_day_share FROM inventory_policy ORDER BY sku""")
    scenario = [[lookup[r.pop("sku")], *r.values()] for r in policy]
    scenario_fields = ["sku_index", "scenario_flag", "demand_status", "on_hand_units", "on_order_units",
        "reserved_units", "lead_time_days", "inventory_position_units", "mean_daily_units", "std_daily_units",
        "safety_stock_units", "reorder_point_units", "target_stock_units", "suggested_order_units", "days_cover",
        "observation_days", "active_sales_days", "largest_day_share"]
    monthly = rows(db, """WITH totals AS (
        SELECT SUBSTR(date,1,7) AS sales_month,SUM(quantity) AS units_sold,
               SUM(revenue_pence) AS sales_pence FROM v_sales GROUP BY 1
        ), comparison AS (
        SELECT *,LAG(units_sold) OVER (ORDER BY sales_month) AS previous_month_units_sold,
        LAG(sales_pence) OVER (ORDER BY sales_month) AS previous_month_sales_pence FROM totals
        ) SELECT sales_month,units_sold,previous_month_units_sold,
        ROUND(100.0*(units_sold-previous_month_units_sold)/NULLIF(previous_month_units_sold,0),2) AS units_mom_pct,
        sales_pence/100.0 AS gross_sales_gbp,previous_month_sales_pence/100.0 AS previous_month_sales_gbp,
        ROUND(100.0*(sales_pence-previous_month_sales_pence)/NULLIF(previous_month_sales_pence,0),2) AS sales_mom_pct
        FROM comparison ORDER BY sales_month""")
    save_csv(ROOT / "reports/monthly_performance.csv", monthly)
    checks = {
        "source_analysis_passed": validation["passed"],
        "all_3789_skus_in_catalog": len(catalog) == 3789,
        "all_3789_skus_in_scenario": len(scenario) == len(catalog),
        "gross_sales_pence": sum(r[4] for r in aggregated) == 965554463,
        "gross_units": sum(r[3] for r in aggregated) == 5263714,
        "credit_pence": sum(r[5] for r in aggregated) == 30438695,
        "orders_disjoint_across_month_country": invoice_conflicts == 0,
        "sales_orders": sum(r[2] for r in orders) == 18957,
        "twelve_months": len(months) == 12,
        "november_sales_growth": monthly[-1]["sales_mom_pct"] == 31.72,
        "manual_review_order_is_null": all(r[13] is None for r in scenario if r[1] == "Manual review"),
    }
    if not all(checks.values()):
        raise ValueError(checks)
    payload = {"meta": {"author": "James You", "start": "2010-12-01", "end": "2011-11-30",
        "snapshot": "2011-11-30", "lookback_days": 90, "currency": "GBP",
        "source": "UCI Online Retail", "license": "CC BY 4.0", "built": "2026-10-21",
        "catalog_fields": list(catalog[0]), "aggregate_fields": ["sku_index", "month_index", "country_index",
            "units", "sales_pence", "credit_pence", "credit_units"], "scenario_fields": scenario_fields},
        "catalog": [list(r.values()) for r in catalog], "months": months, "countries": countries,
        "facts": aggregated, "orders": orders, "scenario": scenario}
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    template = (ROOT / "dashboard/template.html").read_text(encoding="utf-8")
    output = ROOT / "dashboard/index.html"
    output.write_text(template.replace("__PORTFOLIO_DATA__", encoded), encoding="utf-8")
    report = {"passed": all(checks.values()), "checks": checks, "aggregate_rows": len(aggregated),
        "html_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "data_grain": "SKU x calendar month x customer country; no source invoice rows or customer IDs",
        "browser_runtime_test": "Recorded separately in dashboard_runtime_validation.json",
        "powerbi_desktop_validation": "Pending owner Windows refresh and visual confirmation"}
    (ROOT / "reports/portfolio_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "aggregate_rows": len(aggregated),
                      "html_bytes": output.stat().st_size, "november": monthly[-1]}, indent=2))


if __name__ == "__main__":
    build()
