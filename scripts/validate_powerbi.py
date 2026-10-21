"""Validate native PBIP/PBIR JSON against Microsoft's pinned public schemas.

Optional validation dependency: python -m pip install jsonschema
This checks authoring structure and field references, not Desktop execution.
"""
from pathlib import Path
import csv
import hashlib
import json
import tempfile
import urllib.parse
import urllib.request
import warnings

from jsonschema import Draft7Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(tempfile.gettempdir()) / "inventory-portfolio-schemas"
SCHEMAS = {}


def fetch(url):
    url, _ = urllib.parse.urldefrag(url)
    # Some Microsoft embedded schemas declare a dotted $id while the public
    # resource uses a hyphen. Resolve that published alias to the same version.
    url = url.replace("/schema.embedded.json", "/schema-embedded.json")
    if url in SCHEMAS:
        return SCHEMAS[url]
    if not url.startswith("https://developer.microsoft.com/json-schemas/"):
        raise ValueError("Unexpected schema host: " + url)
    CACHE.mkdir(exist_ok=True)
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    if path.exists():
        data = json.loads(path.read_text())
    else:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.load(response)
        path.write_text(json.dumps(data))
    SCHEMAS[url] = data
    return data


def field_references(value):
    if isinstance(value, dict):
        for kind in ["Column", "Measure"]:
            if kind in value:
                item = value[kind]
                source = item.get("Expression", {}).get("SourceRef", {}).get("Entity")
                if source:
                    yield kind, source, item["Property"]
        for item in value.values():
            yield from field_references(item)
    elif isinstance(value, list):
        for item in value:
            yield from field_references(item)


def main():
    errors = []
    checked = 0
    report_dir = ROOT / "powerbi/InventoryPortfolio.Report"
    definition = report_dir / "definition"
    version = json.loads((definition / "version.json").read_text())["version"]
    # JSON Schema accepts any major version; that does not establish Desktop
    # compatibility. Match the official CLI 0.5.0 scaffold's content contract.
    if version != "2.0.0":
        errors.append({"message": "Unexpected PBIR content version; expected scaffold version 2.0.0"})
    if not (report_dir / ".platform").is_file():
        errors.append({"message": "Missing scaffolded report platform metadata"})
    pages = {p.parent.name: json.loads(p.read_text()) for p in (definition / "pages").glob("*/page.json")}
    page_order = json.loads((definition / "pages/pages.json").read_text())["pageOrder"]
    if len(pages) != 3 or set(page_order) != set(pages) or any(name != value["name"] for name, value in pages.items()):
        errors.append({"message": "Expected three page definitions with matching folder names and page order"})
    metadata = json.loads((definition / "report.json").read_text())
    resource_count = 0
    for package in metadata.get("resourcePackages", []):
        for item in package.get("items", []):
            resource = report_dir / "StaticResources" / package["name"] / item["path"]
            resource_count += 1
            if not resource.is_file():
                errors.append({"message": "Missing report resource: " + str(resource.relative_to(ROOT))})
    base_theme = metadata.get("themeCollection", {}).get("baseTheme", {}).get("name")
    if not any(item["name"] == base_theme for package in metadata.get("resourcePackages", []) for item in package.get("items", [])):
        errors.append({"message": "Base theme has no registered resource"})
    for path in sorted((ROOT / "powerbi").rglob("*")):
        if not path.is_file() or (path.suffix not in [".json", ".pbip", ".pbir", ".pbism"] and path.name != ".platform"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        schema_url = data.get("$schema")
        if not schema_url:
            continue
        schema = fetch(schema_url)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            resolver = RefResolver(base_uri=schema_url, referrer=schema, handlers={"https": fetch})
            validator = Draft7Validator(schema, resolver=resolver)
            for error in validator.iter_errors(data):
                errors.append({"file": str(path.relative_to(ROOT)), "path": list(error.absolute_path),
                               "message": error.message})
        checked += 1
    model = json.loads((ROOT / "powerbi/InventoryPortfolio.SemanticModel/model.bim").read_text())["model"]
    tables = {table["name"]: table for table in model["tables"]}
    csv_checks = {}
    expected_rows = {"FactTransactions": 511035, "DimSKU": 3789, "DimDate": 365, "InventoryScenario": 3789}
    for name, table in tables.items():
        import re
        expression = table["partitions"][0]["source"]["expression"]
        match = re.search(r'fxLoadCsv\("([^"]+)"', expression)
        if not match:
            errors.append({"message": "No CSV source for " + name})
            continue
        path = ROOT / "data/processed" / match.group(1)
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            columns = set(reader.fieldnames)
            count = sum(1 for _ in reader)
        needed = {column["sourceColumn"] for column in table["columns"]}
        csv_checks[name] = {"filename": path.name, "rows": count,
            "columns_present": needed <= columns, "row_count_matches": count == expected_rows[name]}
        if not (needed <= columns and count == expected_rows[name]):
            errors.append({"message": "CSV schema/count mismatch for " + name})
    references = 0
    for path in (ROOT / "powerbi/InventoryPortfolio.Report").rglob("visual.json"):
        value = json.loads(path.read_text())
        for kind, table, name in field_references(value):
            known = tables.get(table, {}).get("columns" if kind == "Column" else "measures", [])
            if name not in {item["name"] for item in known}:
                errors.append({"file": str(path.relative_to(ROOT)), "message": "Unknown field: " + table + "." + name})
            references += 1
    for rel in model["relationships"]:
        if rel["crossFilteringBehavior"] != "oneDirection":
            errors.append({"message": "Unexpected bidirectional relationship"})
    if any(r["fromTable"] == "InventoryScenario" and r["toTable"] == "DimDate" for r in model["relationships"]):
        errors.append({"message": "The fixed scenario must not be filtered by the historical calendar"})
    report = {"passed": not errors, "json_documents_checked": checked, "field_references_checked": references,
        "tables": len(tables), "relationships": len(model["relationships"]),
        "measures": sum(len(table.get("measures", [])) for table in tables.values()),
        "pages": len(pages), "pbir_content_version": version, "registered_resources": resource_count,
        "csv_inputs": csv_checks, "schemas": sorted(SCHEMAS), "errors": errors,
        "scope": "Public JSON schema and model-reference validation; not a Power BI Desktop render or DAX engine execution",
        "desktop_evidence_record": "reports/powerbi_desktop_validation.json"}
    (ROOT / "reports/powerbi_source_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
