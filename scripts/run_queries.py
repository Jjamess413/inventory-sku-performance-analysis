"""Run the saved business questions against the generated SQLite database."""
from pathlib import Path
import json
import math
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def statements(text):
    buffer = ""
    for line in text.splitlines():
        buffer += line + "\n"
        if sqlite3.complete_statement(buffer):
            yield buffer
            buffer = ""
    if buffer.strip():
        raise ValueError("SQL file ends with an incomplete statement.")


if __name__ == "__main__":
    database = ROOT / "data/processed/inventory.sqlite"
    if not database.exists():
        raise SystemExit("Run python scripts/build.py first.")
    validation = ROOT / "reports/validation.json"
    if not validation.exists() or not json.loads(validation.read_text()).get("passed", False):
        raise SystemExit("A successful build is required. Inspect reports/validation.json.")
    with sqlite3.connect(database) as connection:
        connection.create_function("SQRT", 1, math.sqrt, deterministic=True)
        connection.create_function("CEIL", 1, math.ceil, deterministic=True)
        query_results = []
        for name in ["02_business_queries.sql", "03_credit_review.sql"]:
            for number, sql in enumerate(statements((ROOT / "sql" / name).read_text()), 1):
                result = pd.read_sql_query(sql, connection)
                query_results.append({"file": name, "statement": number, "result_rows": len(result)})
                print(f"\n{name}, question {number}: {len(result):,} result rows; showing up to 10")
                print(result.head(10).to_string(index=False))
        (ROOT / "reports/query_validation.json").write_text(json.dumps({
            "passed": True, "queries_executed": len(query_results), "queries": query_results
        }, indent=2) + "\n")
