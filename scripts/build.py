"""Build the UCI sales analysis and a separately labelled inventory scenario.

Run from any directory: python scripts/build.py
Raw data, customer identifiers and the generated database are never committed.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
import os
import sqlite3
import sys
import tempfile
import urllib.request
import zipfile

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FACT_COLUMNS = ["source_line_id", "invoice_no", "sku", "date", "quantity",
                "unit_price_pence", "revenue_pence", "country", "transaction_type", "is_exact_repeat"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def acquire_source(config):
    """Download only the publisher's archive; reject changed bytes for review."""
    folder = ROOT / "data/raw"
    folder.mkdir(parents=True, exist_ok=True)
    workbook = folder / "online_retail.xlsx"
    if not workbook.exists():
        archive = folder / "online-retail.zip"
        if not archive.exists():
            with urllib.request.urlopen(config["source_url"], timeout=60) as response:
                archive.write_bytes(response.read())
        if sha256(archive) != config["source_zip_sha256"]:
            raise ValueError("Source archive changed. Review provenance before updating the checksum.")
        with zipfile.ZipFile(archive) as source:
            workbook.write_bytes(source.read("Online Retail.xlsx"))
    if sha256(workbook) != config["source_xlsx_sha256"]:
        raise ValueError("Workbook checksum differs from the reviewed source.")
    return workbook


def classify_transactions(raw):
    """Preserve source rows and explicit exclusions; never silently drop credits."""
    frame = raw.copy()
    frame["source_line_id"] = range(2, len(frame) + 2)  # Excel row, including header.
    frame["is_exact_repeat"] = raw.duplicated(keep="first").astype(int)
    frame["sku"] = frame["StockCode"].astype("string").str.strip().str.upper()
    frame["invoice_no"] = frame["InvoiceNo"].astype("string").str.strip().str.upper()
    frame["Description"] = frame["Description"].astype("string").str.strip()
    frame["date"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce").dt.strftime("%Y-%m-%d")
    frame["quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame["price"] = pd.to_numeric(frame["UnitPrice"], errors="coerce")
    frame["country"] = frame["Country"].fillna("Unknown").astype(str).str.strip()
    # This code-pattern rule is a documented proxy for physical merchandise.
    frame["merchandise_code"] = frame["sku"].str.fullmatch(r"\d{5}[A-Z]{0,2}").fillna(False)
    cancelled = frame["invoice_no"].str.startswith("C", na=False)
    frame["record_type"] = "excluded"
    frame["exclusion_reason"] = "unclassified"
    valid = frame["date"].notna() & frame["quantity"].notna() & frame["price"].gt(0) & frame["merchandise_code"]
    sales = valid & frame["quantity"].gt(0) & ~cancelled
    credits = valid & frame["quantity"].lt(0) & cancelled
    frame.loc[sales, "record_type"] = "sale"
    frame.loc[credits, "record_type"] = "cancellation"
    frame.loc[sales | credits, "exclusion_reason"] = "included"
    # Mutually exclusive reason hierarchy makes the row reconciliation auditable.
    remaining = frame["record_type"].eq("excluded")
    for reason, condition in [
        ("invalid_date_or_quantity", frame["date"].isna() | frame["quantity"].isna()),
        ("nonpositive_or_missing_price", ~frame["price"].gt(0)),
        ("non_merchandise_code", ~frame["merchandise_code"]),
        ("inconsistent_quantity_or_invoice", pd.Series(True, index=frame.index)),
    ]:
        selected = remaining & condition
        frame.loc[selected, "exclusion_reason"] = reason
        remaining &= ~selected
    # GBP minor units avoid floating point drift; rounding is disclosed.
    prices = {p: int((Decimal(str(p)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
              for p in frame.loc[sales | credits, "price"].unique()}
    frame["unit_price_pence"] = frame["price"].map(prices)
    frame["revenue_pence"] = frame["quantity"] * frame["unit_price_pence"]
    return frame


def query(connection, sql):
    return pd.read_sql_query(sql, connection)


def save_csv(frame, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.8f")


def scenario_rows(stats, config):
    """Deterministic SKU hash, not random sampling or confidential stock data."""
    rows = []
    for item in stats.itertuples(index=False):
        seed = int(hashlib.sha256(item.sku.encode()).hexdigest()[:8], 16)
        coverage = (5, 14, 45, 120)[seed % 4]
        on_hand = math.ceil(item.mean_daily_units * coverage)
        if item.recent_units == 0:
            on_hand = 5 + seed % 40
        on_order = math.ceil(item.mean_daily_units * 7) if seed % 3 == 0 else 0
        reserved = min(on_hand, math.floor(item.mean_daily_units * (seed % 3)))
        rows.append({"sku": item.sku, "snapshot_date": config["analysis_end"],
                     "on_hand_units": on_hand, "on_order_units": on_order, "reserved_units": reserved,
                     "lead_time_days": (7, 14, 21)[(seed // 4) % 3], "data_nature": "SYNTHETIC_SCENARIO"})
    return pd.DataFrame(rows)


def build():
    config = json.loads((ROOT / "config.json").read_text())
    processed = ROOT / "data/processed"
    reports = ROOT / "reports"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(exist_ok=True)
    (reports / "validation.json").write_text(json.dumps({"passed": False, "status": "BUILD_IN_PROGRESS"}) + "\n")
    workbook = acquire_source(config)
    print("Reading reviewed UCI workbook...", flush=True)
    raw = pd.read_excel(workbook, dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": str})
    classified = classify_transactions(raw)
    in_period = classified["date"].between(config["analysis_start"], config["analysis_end"])
    selected = classified.loc[in_period & classified.record_type.ne("excluded")].copy()
    selected["transaction_type"] = selected["record_type"]
    # A SKU must have a positive sale in the selected period to enter the model.
    sales = selected.loc[selected.transaction_type.eq("sale")].copy()
    selected = selected.loc[selected.sku.isin(sales.sku.unique())].copy()
    for column in ["quantity", "unit_price_pence", "revenue_pence"]:
        selected[column] = selected[column].astype("int64")
    dimensions = sales.groupby("sku")["date"].agg(first_sale_date="min", last_sale_date="max").reset_index()
    labels = (sales.loc[sales.Description.notna() & sales.Description.ne("")]
              .sort_values(["InvoiceDate", "source_line_id"]).drop_duplicates("sku", keep="last")
              [["sku", "Description"]].rename(columns={"Description": "description"}))
    dimensions = dimensions.merge(labels, on="sku", how="left", validate="one_to_one")
    dimensions["description"] = dimensions["description"].fillna("Description unavailable")
    dimensions = dimensions[["sku", "description", "first_sale_date", "last_sale_date"]]
    dates = pd.date_range(config["analysis_start"], config["analysis_end"])
    calendar = pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "month": dates.strftime("%Y-%m"),
                             "year": dates.year, "month_number": dates.month, "day_of_week": dates.dayofweek})
    database = processed / "inventory.sqlite"
    # Use a distinct journal path while building. Existing query readers keep
    # their old database; the finished, validated file is installed at the end.
    descriptor, staging_name = tempfile.mkstemp(prefix="inventory-build-", suffix=".sqlite", dir=processed)
    os.close(descriptor)
    staging_database = Path(staging_name)
    connection = sqlite3.connect(staging_database)
    connection.create_function("SQRT", 1, math.sqrt, deterministic=True)
    connection.create_function("CEIL", 1, math.ceil, deterministic=True)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript((ROOT / "sql/00_schema.sql").read_text())
    parameters = {key: config[key] for key in ["analysis_start", "analysis_end", "lookback_days",
                  "minimum_active_days", "service_z", "order_cycle_days", "excess_cover_days"]}
    parameters["lookback_start"] = (pd.Timestamp(config["analysis_end"]) - pd.Timedelta(days=config["lookback_days"] - 1)).strftime("%Y-%m-%d")
    pd.DataFrame([parameters]).to_sql("parameters", connection, if_exists="append", index=False)
    calendar.to_sql("dim_date", connection, if_exists="append", index=False)
    dimensions.to_sql("dim_sku", connection, if_exists="append", index=False)
    selected[FACT_COLUMNS].to_sql("fact_transactions", connection, if_exists="append", index=False, chunksize=10000)
    connection.executescript((ROOT / "sql/01_analysis_views.sql").read_text())
    print("Calculating calendar-based demand and synthetic scenario...", flush=True)
    stats = query(connection, "SELECT * FROM v_demand_stats ORDER BY sku")
    snapshot = scenario_rows(stats, config)
    snapshot.to_sql("synthetic_inventory_snapshot", connection, if_exists="append", index=False)
    connection.commit()
    # Materialised derived tables make later dashboard reads quick and explicit.
    for table, view in [("sku_abc", "v_abc"), ("inventory_policy", "v_inventory_policy")]:
        connection.execute(f"CREATE TABLE {table} AS SELECT * FROM {view}")
    connection.commit()
    sales_fact = query(connection, "SELECT * FROM fact_transactions ORDER BY source_line_id")
    abc = query(connection, "SELECT * FROM sku_abc ORDER BY revenue_rank")
    policy = query(connection, "SELECT * FROM inventory_policy ORDER BY sku")
    dim_export = dimensions.merge(abc[["sku", "abc_class"]], on="sku", validate="one_to_one")
    for name, frame in [("fact_transactions", sales_fact), ("dim_sku", dim_export), ("dim_date", calendar),
                        ("inventory_scenario", policy), ("demand_stats", stats)]:
        save_csv(frame, processed / f"{name}.csv")
    save_csv(snapshot, ROOT / "data/synthetic/inventory_snapshot.csv")
    queries = {
        "kpi_summary": """SELECT COUNT(*) AS transaction_lines,
          SUM(CASE WHEN transaction_type='sale' THEN 1 ELSE 0 END) AS sale_lines,
          COUNT(DISTINCT CASE WHEN transaction_type='sale' THEN invoice_no END) AS sales_orders,
          COUNT(DISTINCT sku) AS skus, SUM(CASE WHEN transaction_type='sale' THEN quantity ELSE 0 END) AS gross_units,
          SUM(CASE WHEN transaction_type='sale' THEN revenue_pence ELSE 0 END)/100.0 AS gross_sales_gbp,
          -SUM(CASE WHEN transaction_type='cancellation' THEN revenue_pence ELSE 0 END)/100.0 AS cancellation_value_gbp,
          SUM(revenue_pence)/100.0 AS signed_transaction_value_gbp FROM fact_transactions""",
        "abc_summary": "SELECT abc_class, COUNT(*) AS sku_count, SUM(units_sold) AS units_sold, SUM(gross_revenue_pence)/100.0 AS gross_sales_gbp, SUM(revenue_share)*100 AS sales_share_pct FROM sku_abc GROUP BY abc_class ORDER BY abc_class",
        "monthly_sales": "SELECT SUBSTR(date,1,7) AS month, SUM(quantity) AS units_sold, SUM(revenue_pence)/100.0 AS gross_sales_gbp FROM v_sales GROUP BY SUBSTR(date,1,7) ORDER BY month",
        "top_revenue_skus": "SELECT a.sku, d.description, a.units_sold, a.gross_revenue_pence/100.0 AS gross_sales_gbp, a.abc_class FROM sku_abc a INNER JOIN dim_sku d ON a.sku=d.sku ORDER BY a.revenue_rank LIMIT 10",
        "lowest_volume_skus": "SELECT a.sku, d.description, a.units_sold, a.gross_revenue_pence/100.0 AS gross_sales_gbp FROM sku_abc a INNER JOIN dim_sku d ON a.sku=d.sku ORDER BY a.units_sold, a.sku LIMIT 10",
        "scenario_summary": "SELECT scenario_flag, COUNT(*) AS sku_count, SUM(CASE WHEN abc_class='A' THEN 1 ELSE 0 END) AS class_a_skus FROM inventory_policy GROUP BY scenario_flag ORDER BY scenario_flag",
        "demand_eligibility": "SELECT demand_status, COUNT(*) AS sku_count FROM inventory_policy GROUP BY demand_status ORDER BY demand_status",
        "same_day_offset_candidates": """SELECT sku, date, ABS(quantity) AS units_per_line, unit_price_pence/100.0 AS unit_price_gbp,
          SUM(CASE WHEN transaction_type='sale' THEN 1 ELSE 0 END) AS positive_lines,
          SUM(CASE WHEN transaction_type='cancellation' THEN 1 ELSE 0 END) AS negative_lines,
          MIN(SUM(CASE WHEN transaction_type='sale' THEN 1 ELSE 0 END), SUM(CASE WHEN transaction_type='cancellation' THEN 1 ELSE 0 END))
             * ABS(quantity) * unit_price_pence / 100.0 AS possible_offset_value_gbp
          FROM fact_transactions GROUP BY sku,date,ABS(quantity),unit_price_pence
          HAVING SUM(CASE WHEN transaction_type='sale' THEN 1 ELSE 0 END)>0
             AND SUM(CASE WHEN transaction_type='cancellation' THEN 1 ELSE 0 END)>0
          ORDER BY possible_offset_value_gbp DESC,sku,date""",
        "sku_credit_review": """SELECT f.sku,d.description,
          SUM(CASE WHEN f.transaction_type='sale' THEN f.quantity ELSE 0 END) AS gross_units,
          -SUM(CASE WHEN f.transaction_type='cancellation' THEN f.quantity ELSE 0 END) AS credited_units,
          SUM(CASE WHEN f.transaction_type='sale' THEN f.revenue_pence ELSE 0 END)/100.0 AS gross_sales_gbp,
          -SUM(CASE WHEN f.transaction_type='cancellation' THEN f.revenue_pence ELSE 0 END)/100.0 AS credit_value_gbp,
          SUM(f.revenue_pence)/100.0 AS signed_transaction_value_gbp
          FROM fact_transactions f INNER JOIN dim_sku d ON f.sku=d.sku
          GROUP BY f.sku,d.description ORDER BY credit_value_gbp DESC,f.sku LIMIT 25""",
        "scenario_review_queue": "SELECT p.sku, d.description, p.abc_class, p.scenario_flag, p.demand_status, p.mean_daily_units, p.std_daily_units, p.on_hand_units, p.on_order_units, p.reserved_units, p.lead_time_days, p.inventory_position_units, p.safety_stock_units, p.reorder_point_units, p.target_stock_units, p.suggested_order_units, p.days_cover, p.data_nature FROM inventory_policy p INNER JOIN dim_sku d ON p.sku=d.sku ORDER BY p.abc_class,p.gross_revenue_pence DESC,p.sku",
    }
    for name, sql in queries.items():
        save_csv(query(connection, sql), reports / f"{name}.csv")
    quality = {
        "source_rows": len(raw), "source_columns": list(raw.columns),
        "source_missing_values": raw.isna().sum().astype(int).to_dict(),
        "exact_repeat_rows_retained": int(raw.duplicated().sum()),
        "source_min_date": str(raw.InvoiceDate.min()), "source_max_date": str(raw.InvoiceDate.max()),
        "classification_all_dates": classified.record_type.value_counts().to_dict(),
        "exclusion_reasons_all_dates": classified.exclusion_reason.value_counts().to_dict(),
        "rows_outside_analysis_period": int((~in_period).sum()),
        "in_period_excluded_rows": int((in_period & classified.record_type.eq("excluded")).sum()),
        "in_period_credit_rows_without_positive_sale_sku": int((in_period & classified.record_type.eq("cancellation") & ~classified.sku.isin(dimensions.sku)).sum()),
        "model_rows": len(sales_fact), "model_skus": len(dimensions),
        "duplicate_policy": "Retain exact repeats: the source has no unique invoice-line key.",
        "customer_id_policy": "Excluded from every model table, export and public report.",
        "source_zip_sha256": config["source_zip_sha256"], "source_xlsx_sha256": sha256(workbook),
        "price_rounding": "Round each unit price to GBP pence, ROUND_HALF_UP, before multiplying by quantity.",
        "source_prices_with_subpenny_precision": int((raw.UnitPrice.mul(100).sub(raw.UnitPrice.mul(100).round()).abs() > 1e-7).sum()),
        "sales_gbp_if_exact_repeats_removed": round(float(sales.loc[sales.is_exact_repeat.eq(0), "revenue_pence"].sum()) / 100, 2),
    }
    checks = {
        "source_row_reconciliation": len(raw) == quality["rows_outside_analysis_period"] + quality["in_period_excluded_rows"] + quality["in_period_credit_rows_without_positive_sale_sku"] + len(sales_fact),
        "foreign_key_integrity": connection.execute("PRAGMA foreign_key_check").fetchall() == [],
        "sqlite_integrity": connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
        "gross_revenue_reconciles_pandas_sql": int(sales.revenue_pence.sum()) == int(abc.gross_revenue_pence.sum()),
        "gross_units_reconcile": int(sales.quantity.sum()) == int(abc.units_sold.sum()),
        "one_sku_per_dimension": not dimensions.sku.duplicated().any(),
        "abc_complete": len(abc) == len(dimensions) and abs(abc.revenue_share.sum() - 1) < 1e-10,
        "one_snapshot_per_sku": len(snapshot) == len(dimensions) and not snapshot.sku.duplicated().any(),
        "all_inventory_labelled_synthetic": snapshot.data_nature.eq("SYNTHETIC_SCENARIO").all(),
        "manual_review_has_no_order_recommendation": policy.loc[policy.demand_status.ne("Eligible for baseline"), "suggested_order_units"].isna().all(),
        "concentrated_sales_require_review": policy.loc[policy.largest_day_share.ge(0.5), "suggested_order_units"].isna().all(),
        "eligible_history_is_full_lookback": policy.loc[policy.demand_status.eq("Eligible for baseline"), "observation_days"].eq(config["lookback_days"]).all(),
        "customer_identifiers_not_exported": all("CustomerID" not in x.columns for x in [sales_fact, dim_export, policy]),
        "twelve_complete_months": len(calendar.month.unique()) == 12 and len(calendar) == 365,
    }
    validation = {"checks": {k: bool(v) for k, v in checks.items()}, "passed": all(checks.values()),
                  "runtime": {"python": sys.version.split()[0], "pandas": pd.__version__, "sqlite": sqlite3.sqlite_version},
                  "analysis_parameters": parameters}
    (reports / "data_quality.json").write_text(json.dumps(quality, indent=2) + "\n")
    connection.close()
    if not validation["passed"]:
        (reports / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
        raise AssertionError("Validation failed; inspect reports/validation.json before using results.")
    staging_database.replace(database)
    (reports / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks), "model_rows": len(sales_fact),
                      "model_skus": len(dimensions), "database": str(database)}, indent=2))


if __name__ == "__main__":
    build()
