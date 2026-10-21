"""Point the portable Power BI model at this folder's reviewed CSVs, then open it."""
from pathlib import Path
import argparse
import json
import os

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    folder = ROOT / "data/processed"
    expected = ["fact_transactions.csv", "dim_sku_portfolio.csv", "dim_date.csv", "inventory_scenario.csv"]
    missing = [name for name in expected if not (folder / name).is_file()]
    if missing:
        raise SystemExit("Missing CSVs: " + ", ".join(missing) +
                         ". Run scripts/build.py, then scripts/build_dashboard.py first.")
    report_dir = ROOT / "powerbi/InventoryPortfolio.Report"
    definition = report_dir / "definition"
    version = json.loads((definition / "version.json").read_text(encoding="utf-8"))["version"]
    order = json.loads((definition / "pages/pages.json").read_text(encoding="utf-8"))["pageOrder"]
    if not (report_dir / ".platform").is_file() or version != "2.0.0" or len(order) != 3 or any(not (definition / "pages" / page / "page.json").is_file() for page in order):
        raise SystemExit("Report layout is incomplete or incompatible. Extract the full corrected ZIP into a new folder.")
    report = json.loads((definition / "report.json").read_text(encoding="utf-8"))
    for package in report.get("resourcePackages", []):
        for item in package.get("items", []):
            if not (report_dir / "StaticResources" / package["name"] / item["path"]).is_file():
                raise SystemExit("Report theme resources are missing. Extract the full corrected ZIP.")
    path = ROOT / "powerbi/InventoryPortfolio.SemanticModel/model.bim"
    model = json.loads(path.read_text(encoding="utf-8"))
    parameter = next(x for x in model["model"]["expressions"] if x["name"] == "pDataFolder")
    value = folder.resolve().as_posix().replace('"', '""') + "/"
    parameter["expression"] = '"' + value + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
    path.write_text(json.dumps(model, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Data folder configured:", folder.resolve())
    print("Report layout checked: three pages and registered theme resources.")
    print("Open InventoryPortfolio.pbip, click Refresh, and compare the totals in START_HERE.md.")
    if os.name == "nt" and not args.prepare_only:
        os.startfile(str(ROOT / "powerbi/InventoryPortfolio.pbip"))


if __name__ == "__main__":
    main()
