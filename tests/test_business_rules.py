"""Small hand-calculated fixtures check the decisions that can distort results."""
import importlib.util
import math
from pathlib import Path
import sqlite3
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts/build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


def source_row(**overrides):
    row = {"InvoiceNo": "123456", "StockCode": "12345A", "Description": "Example gift",
           "Quantity": 2, "InvoiceDate": pd.Timestamp("2020-01-01"), "UnitPrice": 2.50,
           "CustomerID": None, "Country": "United Kingdom"}
    row.update(overrides)
    return row


class CleaningTests(unittest.TestCase):
    def test_missing_customer_id_does_not_remove_sale(self):
        result = build.classify_transactions(pd.DataFrame([source_row()]))
        self.assertEqual(result.record_type.tolist(), ["sale"])
        self.assertEqual(result.revenue_pence.tolist(), [500])

    def test_repeated_rows_are_flagged_and_retained(self):
        result = build.classify_transactions(pd.DataFrame([source_row(), source_row()]))
        self.assertEqual(result.is_exact_repeat.tolist(), [0, 1])
        self.assertEqual(result.record_type.tolist(), ["sale", "sale"])

    def test_cancellation_is_negative_and_separate(self):
        result = build.classify_transactions(pd.DataFrame([source_row(InvoiceNo="C123456", Quantity=-2)]))
        self.assertEqual(result.record_type.iloc[0], "cancellation")
        self.assertEqual(result.revenue_pence.iloc[0], -500)

    def test_free_items_postage_and_unmatched_negative_entries_are_not_sales(self):
        rows = [source_row(UnitPrice=0), source_row(StockCode="POST"), source_row(Quantity=-1)]
        result = build.classify_transactions(pd.DataFrame(rows))
        self.assertEqual(result.record_type.tolist(), ["excluded"] * 3)
        self.assertEqual(result.exclusion_reason.tolist(), ["nonpositive_or_missing_price", "non_merchandise_code", "inconsistent_quantity_or_invoice"])

    def test_subpenny_price_rounds_half_up_before_quantity(self):
        result = build.classify_transactions(pd.DataFrame([source_row(UnitPrice=2.675)]))
        self.assertEqual(result.unit_price_pence.iloc[0], 268)
        self.assertEqual(result.revenue_pence.iloc[0], 536)


class SQLTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.create_function("SQRT", 1, math.sqrt)
        self.connection.create_function("CEIL", 1, math.ceil)
        self.connection.executescript((ROOT / "sql/00_schema.sql").read_text())
        self.connection.execute("INSERT INTO parameters VALUES ('2020-01-01','2020-01-03','2020-01-01',3,1,1.645,7,90)")
        self.connection.executemany("INSERT INTO dim_date VALUES (?, '2020-01', 2020, 1, 1)",
                                    [(f"2020-01-0{i}",) for i in range(1, 4)])
        self.connection.executescript((ROOT / "sql/01_analysis_views.sql").read_text())

    def tearDown(self):
        self.connection.close()

    def add_product(self, sku, revenue, units=1, row_number=1):
        self.connection.execute("INSERT INTO dim_sku VALUES (?, 'Fixture', '2020-01-01', '2020-01-01')", (sku,))
        self.connection.execute("INSERT INTO fact_transactions VALUES (?, ?, ?, '2020-01-01', ?, ?, ?, 'UK', 'sale', 0)",
                                (row_number, str(row_number), sku, units, revenue, units * revenue))

    def test_abc_includes_threshold_crossing_sku(self):
        for number, value in enumerate([60, 25, 10, 5], 1):
            self.add_product(str(number), value, row_number=number)
        actual = self.connection.execute("SELECT sku, abc_class FROM v_abc ORDER BY revenue_rank").fetchall()
        self.assertEqual(actual, [("1", "A"), ("2", "A"), ("3", "B"), ("4", "C")])

    def test_no_sale_days_are_included_in_mean_and_sample_std(self):
        self.add_product("1", 100, units=3)
        days, mean, std = self.connection.execute("SELECT observation_days, mean_daily_units, std_daily_units FROM v_demand_stats").fetchone()
        self.assertEqual(days, 3)
        self.assertEqual(mean, 1.0)  # Sales [3, 0, 0], not just [3].
        self.assertAlmostEqual(std, math.sqrt(3))

    def test_manual_review_has_no_automatic_reorder(self):
        self.add_product("1", 100, units=3)
        self.connection.execute("UPDATE parameters SET minimum_active_days = 2")
        self.connection.execute("INSERT INTO synthetic_inventory_snapshot VALUES ('1', '2020-01-03', 0, 0, 0, 7, 'SYNTHETIC_SCENARIO')")
        status, order = self.connection.execute("SELECT scenario_flag, suggested_order_units FROM v_inventory_policy").fetchone()
        self.assertEqual(status, "Manual review")
        self.assertIsNone(order)

    def test_single_day_concentration_requires_review(self):
        self.add_product("1", 100, units=100)
        for day in [2, 3]:
            self.connection.execute("INSERT INTO fact_transactions VALUES (?, ?, '1', ?, 1, 100, 100, 'UK', 'sale', 0)",
                                    (day, str(day), f"2020-01-0{day}"))
        status = self.connection.execute("SELECT demand_status FROM v_demand_stats").fetchone()[0]
        self.assertEqual(status, "Concentrated sales")

    def test_scenario_is_reproducible(self):
        stats = pd.DataFrame([{"sku": "1", "mean_daily_units": 1.5, "recent_units": 135}])
        first = build.scenario_rows(stats, {"analysis_end": "2020-01-03"})
        second = build.scenario_rows(stats, {"analysis_end": "2020-01-03"})
        pd.testing.assert_frame_equal(first, second)
        self.assertEqual(first.data_nature.iloc[0], "SYNTHETIC_SCENARIO")


if __name__ == "__main__":
    unittest.main()
