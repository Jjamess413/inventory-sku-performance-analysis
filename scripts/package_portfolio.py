"""Create the portable project package without raw workbooks, identities or caches."""
from pathlib import Path
import argparse
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist/James_You_Inventory_Portfolio.zip")
    args = parser.parse_args()
    for report in ["validation.json", "query_validation.json", "portfolio_validation.json", "dashboard_runtime_validation.json",
                   "powerbi_source_validation.json", "powerbi_cli_validation.json"]:
        data = json.loads((ROOT / "reports" / report).read_text())
        if data.get("passed") is not True:
            raise SystemExit("Acceptance report has not passed: " + report)
    files = {ROOT / name for name in ["README.md", "START_HERE.md", "OPEN_POWERBI.cmd",
             "DATA_ATTRIBUTION.md", "requirements.txt", "config.json", "data/README.md"]}
    for directory in ["powerbi", "scripts", "sql", "docs", "reports", "tests", "data/synthetic"]:
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and ".pbi" not in path.parts:
                files.add(path)
    for name in ["index.html", "template.html", "README.md"]:
        files.add(ROOT / "dashboard" / name)
    for name in ["inventory.sqlite", "fact_transactions.csv", "dim_sku.csv", "dim_sku_portfolio.csv",
                 "dim_date.csv", "inventory_scenario.csv", "demand_stats.csv"]:
        path = ROOT / "data/processed" / name
        if not path.is_file():
            raise SystemExit("Missing portable input: " + str(path))
        files.add(path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    prefix = "James_You_Inventory_Portfolio"
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(files):
            name = (Path(prefix) / path.relative_to(ROOT)).as_posix()
            if path == ROOT / "README.md":
                archive.writestr(name,
                    "# Inventory & SKU Performance — portable package\n\n"
                    "Start with START_HERE.md. Open dashboard/index.html for the completed offline report, "
                    "or double-click OPEN_POWERBI.cmd and refresh the authored native Power BI project.\n\n"
                    "Native Desktop confirmation is the final acceptance step. The included reports document "
                    "completed data, browser and source-structure checks separately.\n\n"
                    "Full repository, case study and actual browser captures:\n"
                    "https://github.com/Jjamess413/inventory-sku-performance-analysis\n\n"
                    "Source: UCI Online Retail (Chen, 2015), DOI 10.24432/C5BW33, CC BY 4.0. "
                    "All stock balances and supplier lead times are labelled synthetic assumptions.\n")
            else:
                archive.write(path, name)
    with zipfile.ZipFile(args.output) as archive:
        bad = archive.testzip()
        if bad:
            raise SystemExit("Archive failed CRC validation: " + bad)
        names = archive.namelist()
        if any("/data/raw/" in name or "/.git/" in name or "/.pbi/" in name for name in names):
            raise SystemExit("Unexpected raw/cache/version-control content")
    print(json.dumps({"status": "PASS", "output": str(args.output.resolve()), "files": len(files),
        "bytes": args.output.stat().st_size, "raw_workbook_included": False,
        "customer_id_column_in_model": False,
        "desktop_powerbi_acceptance": "Pending Windows refresh and actual visual confirmation"}, indent=2))


if __name__ == "__main__":
    main()
