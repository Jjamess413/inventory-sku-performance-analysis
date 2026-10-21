"""Generate a native PBIP report and import model using Microsoft's public formats.

This is authoring, not Desktop execution. Windows refresh/visual QA is recorded
separately. Run build.py and build_dashboard.py before opening the report.
"""
from pathlib import Path
import json
import re
import uuid

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
REPORT = PBI / "InventoryPortfolio.Report"
MODEL = PBI / "InventoryPortfolio.SemanticModel"
BASE = "https://developer.microsoft.com/json-schemas/fabric/"
NAVY, TEAL, INK, MUTED = "#102235", "#087E78", "#182B3D", "#627486"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def identity(value):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "james-you-inventory/" + value))


def parse_measures():
    result = {}
    name, lines = None, []
    for line in (PBI / "measures.dax").read_text().splitlines():
        if line.strip().startswith("//"):
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9 %&-]+)\s*=\s*", line)
        if match:
            if name:
                result[name] = "\n".join(lines).strip()
            name, lines = match.group(1).strip(), []
        elif name:
            lines.append(line)
    if name:
        result[name] = "\n".join(lines).strip()
    result.update({
        "ABC Share of Sales": "DIVIDE([Gross Merchandise Sales GBP], CALCULATE([Gross Merchandise Sales GBP], REMOVEFILTERS(DimSKU[abc_class])))",
        "Top Ten SKU Sales GBP": "IF(SELECTEDVALUE(DimSKU[revenue_rank], 999999) <= 10, [Gross Merchandise Sales GBP])",
        "SKU Units Rank": "IF(NOT ISBLANK([Gross Units]), RANKX(ALLSELECTED(DimSKU), [Gross Units], , DESC, DENSE))",
        "Top Ten SKU Units": "IF([SKU Units Rank] <= 10, [Gross Units])",
        "Previous Month Sales GBP": "CALCULATE([Gross Merchandise Sales GBP], DATEADD(DimDate[date], -1, MONTH))",
        "Sales MoM %": "DIVIDE([Gross Merchandise Sales GBP] - [Previous Month Sales GBP], [Previous Month Sales GBP])",
        "Previous Month Units": "CALCULATE([Gross Units], DATEADD(DimDate[date], -1, MONTH))",
        "Units MoM %": "DIVIDE([Gross Units] - [Previous Month Units], [Previous Month Units])",
    })
    return result


def build_model():
    measures = parse_measures()
    schema = {
        "FactTransactions": [
            ("source_line_id", "int64"), ("invoice_no", "string"), ("sku", "string"),
            ("date", "dateTime"), ("quantity", "int64"), ("unit_price_pence", "int64"),
            ("revenue_pence", "int64"), ("country", "string"), ("transaction_type", "string"),
            ("is_exact_repeat", "int64")],
        "DimSKU": [("sku", "string"), ("description", "string"), ("first_sale_date", "dateTime"),
            ("last_sale_date", "dateTime"), ("abc_class", "string"), ("revenue_rank", "int64"),
            ("product_label", "string")],
        "DimDate": [("date", "dateTime"), ("month", "string"), ("year", "int64"),
            ("month_number", "int64"), ("day_of_week", "int64")],
        "InventoryScenario": [("sku", "string"), ("snapshot_date", "dateTime"),
            ("data_nature", "string"), ("on_hand_units", "int64"), ("on_order_units", "int64"),
            ("reserved_units", "int64"), ("lead_time_days", "int64"),
            ("inventory_position_units", "int64"), ("mean_daily_units", "double"),
            ("std_daily_units", "double"), ("days_cover", "double"),
            ("safety_stock_units", "int64"), ("reorder_point_units", "int64"),
            ("target_stock_units", "int64"), ("suggested_order_units", "int64"),
            ("demand_status", "string"), ("scenario_flag", "string"), ("abc_class", "string")],
    }
    tables = []
    for table, fields in schema.items():
        columns = []
        for name, typ in fields:
            column = {"name": name, "dataType": typ, "sourceColumn": name,
                "lineageTag": identity(table + "/" + name), "summarizeBy": "none"}
            if typ == "dateTime":
                column["formatString"] = "yyyy-MM-dd"
            elif typ == "int64":
                column["formatString"] = "#,0"
            elif typ == "double":
                column["formatString"] = "0.00"
            if (table == "DimSKU" and name == "sku") or (table == "DimDate" and name == "date"):
                column["isKey"] = True
            if table == "FactTransactions" and name in ["source_line_id", "unit_price_pence", "revenue_pence", "is_exact_repeat"]:
                column["isHidden"] = True
            columns.append(column)
        expression = (PBI / "powerquery" / (table + ".pq")).read_text()
        definition = {"name": table, "lineageTag": identity(table), "columns": columns,
            "partitions": [{"name": table, "mode": "import", "source": {"type": "m", "expression": expression}}],
            "annotations": [{"name": "PBI_ResultType", "value": "Table"}]}
        if table == "DimDate":
            definition["dataCategory"] = "Time"
        if table == "FactTransactions":
            definition["measures"] = []
            for name, expression in measures.items():
                measure = {"name": name, "expression": expression, "lineageTag": identity("measure/" + name)}
                if "GBP" in name:
                    measure["formatString"] = "£#,0.00;(£#,0.00);£0.00"
                elif "%" in name or name == "ABC Share of Sales":
                    measure["formatString"] = "0.00%"
                elif name != "Scenario Label":
                    measure["formatString"] = "#,0.00" if name == "Average Units Per Order" else "#,0"
                measure["displayFolder"] = "Scenario (synthetic)" if name.startswith("Scenario") else "Historical sales"
                definition["measures"].append(measure)
        tables.append(definition)
    relationships = []
    for from_table, from_column, to_table, to_column in [
        ("FactTransactions", "sku", "DimSKU", "sku"),
        ("FactTransactions", "date", "DimDate", "date"),
        ("InventoryScenario", "sku", "DimSKU", "sku")]:
        relationships.append({"name": identity(from_table + "/" + from_column + "->" + to_table),
            "fromTable": from_table, "fromColumn": from_column, "toTable": to_table,
            "toColumn": to_column, "fromCardinality": "many", "toCardinality": "one",
            "crossFilteringBehavior": "oneDirection", "isActive": True})
    model = {"name": "InventoryPortfolio", "compatibilityLevel": 1567, "model": {
        "culture": "en-GB", "sourceQueryCulture": "en-GB",
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "tables": tables, "relationships": relationships,
        "expressions": [
            {"name": "pDataFolder", "kind": "m", "expression": '"C:/InventoryPortfolio/data/processed/" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'},
            {"name": "fxLoadCsv", "kind": "m", "expression": (PBI / "powerquery/fxLoadCsv.pq").read_text()}],
        "annotations": [{"name": "PBI_TimeIntelligenceEnabled", "value": "0"},
                        {"name": "PortfolioDataNature", "value": "Public historical sales; inventory balances and lead times are synthetic"}]}}
    write(MODEL / "model.bim", model)
    (PBI / "all_measures.dax").write_text(
        "// Authored model definitions; native Desktop execution is confirmed separately.\n\n" +
        "\n\n".join(name + " =\n" + expression for name, expression in measures.items()) + "\n",
        encoding="utf-8")
    write(MODEL / "definition.pbism", {"$schema": BASE + "item/semanticModel/definitionProperties/1.0.0/schema.json",
                                      "version": "1.0", "settings": {"qnaEnabled": False}})
    return schema, measures


def literal(value):
    if isinstance(value, bool):
        value = "true" if value else "false"
    elif isinstance(value, (int, float)):
        value = str(value) + "D"
    else:
        value = "'" + str(value).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": value}}}


def color(value):
    return {"solid": {"color": literal(value)}}


def field(table, name, measure=False):
    return {("Measure" if measure else "Column"): {
        "Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


def projection(table, name, measure=False, display=None):
    value = {"field": field(table, name, measure), "queryRef": table + "." + name,
             "nativeQueryRef": name}
    if display:
        value["displayName"] = display
    return value


def container(title, background="#FFFFFF"):
    return {
        "title": [{"properties": {"show": literal(bool(title)), "text": literal(title),
            "fontColor": color(INK), "fontSize": literal(12), "bold": literal(True),
            "fontFamily": literal("Segoe UI")}}],
        "background": [{"properties": {"show": literal(True), "color": color(background), "transparency": literal(0)}}],
        "border": [{"properties": {"show": literal(True), "color": color("#DCE5EB"), "radius": literal(8)}}],
    }


def visual(page, name, kind, x, y, w, h, title="", roles=None, sort=None, objects=None):
    content = {"visualType": kind, "visualContainerObjects": container(title)}
    if roles:
        content["query"] = {"queryState": {role: {"projections": values} for role, values in roles.items()}}
        if sort:
            content["query"]["sortDefinition"] = {"sort": [{"field": sort[0], "direction": sort[1]}],
                                                   "isDefaultSort": False}
    if objects:
        content["objects"] = objects
    value = {"$schema": BASE + "item/report/definition/visualContainer/2.4.0/schema.json",
        "name": name, "position": {"x": x, "y": y, "z": y, "width": w, "height": h, "tabOrder": y},
        "visual": content}
    write(REPORT / "definition/pages" / page / "visuals" / name / "visual.json", value)


def textbox(page, name, text, x, y, w, h, size=12, foreground=INK, background="#FFFFFF"):
    visual(page, name, "textbox", x, y, w, h, objects={
        "general": [{"properties": {"paragraphs": [
            {"textRuns": [{"value": line, "textStyle": {"fontFamily": "Segoe UI",
                "fontSize": str(size) + "pt", "color": foreground}}]} for line in text.split("\n")
        ]}}]})
    path = REPORT / "definition/pages" / page / "visuals" / name / "visual.json"
    value = json.loads(path.read_text())
    value["visual"]["visualContainerObjects"] = container("", background)
    write(path, value)


def build_report():
    write(PBI / "InventoryPortfolio.pbip", {"$schema": BASE + "pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": "InventoryPortfolio.Report"}}],
        "settings": {"enableAutoRecovery": True}})
    write(REPORT / "definition.pbir", {"$schema": BASE + "item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../InventoryPortfolio.SemanticModel"}}})
    # Match Microsoft's report-authoring CLI scaffold. The project binding's
    # version (4.0) is distinct from the report content version (2.0.0).
    write(REPORT / ".platform", {
        "$schema": BASE + "gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": "InventoryPortfolio"},
        "config": {"version": "2.0", "logicalId": identity("report-platform")}})
    write(REPORT / "definition/version.json", {
        "$schema": BASE + "item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write(REPORT / "definition/report.json", {
        "$schema": BASE + "item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {"baseTheme": {"name": "Fluent2-CY26SU10",
            "reportVersionAtImport": {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"},
            "type": "SharedResources"}},
        "resourcePackages": [{"name": "SharedResources", "type": "SharedResources", "items": [{
            "name": "Fluent2-CY26SU10", "path": "BaseThemes/Fluent2-CY26SU10.json", "type": "BaseTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True, "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True, "useDefaultAggregateDisplayName": True},
        "annotations": [{"name": "AuthoringStatus", "value": "Automated checks cover source structure. See reports/powerbi_desktop_validation.json for owner-run Desktop evidence."}]})
    pages = [("ExecutiveOverview", "01 Executive Overview"),
             ("SKUPerformance", "02 SKU Performance"),
             ("StockReviewScenario", "03 Stock Review - Synthetic")]
    write(REPORT / "definition/pages/pages.json", {
        "$schema": BASE + "item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [name for name, _ in pages], "activePageName": pages[0][0]})
    for name, label in pages:
        write(REPORT / "definition/pages" / name / "page.json", {
            "$schema": BASE + "item/report/definition/page/1.0.0/schema.json",
            "name": name, "displayName": label, "displayOption": "FitToPage", "width": 1280, "height": 900,
            "objects": {"background": [{"properties": {"color": color("#F3F6F8"), "transparency": literal(0)}}]}})
    measure = lambda name, display=None: projection("FactTransactions", name, True, display)
    column = lambda table, name, display=None: projection(table, name, False, display)
    card_options = {"labels": [{"properties": {"color": color(INK), "fontSize": literal(27), "labelDisplayUnits": literal(1)}}],
                    "categoryLabels": [{"properties": {"show": literal(False)}}]}
    p = "ExecutiveOverview"
    textbox(p, "Header", "INVENTORY & SKU PERFORMANCE", 24, 16, 1232, 70, 25, "#FFFFFF", NAVY)
    textbox(p, "Scope", "James You | Historical public retail sales | GBP | Dec 2010 - Nov 2011", 24, 94, 900, 40, 12, MUTED)
    visual(p, "MonthSlicer", "slicer", 938, 92, 150, 55, "Sales month",
           {"Values": [column("DimDate", "month")]})
    visual(p, "CountrySlicer", "slicer", 1100, 92, 156, 55, "Country",
           {"Values": [column("FactTransactions", "country")]})
    for i, (name, title) in enumerate([("Gross Merchandise Sales GBP", "Gross merchandise sales"),
        ("Gross Units", "Gross units"), ("Sales Orders", "Sales orders"), ("Active SKUs", "Active SKUs")]):
        visual(p, "KPI" + str(i), "card", 24 + 314*i, 164, 290, 105, title,
               {"Values": [measure(name)]}, objects=card_options)
    visual(p, "MonthlySales", "lineChart", 24, 288, 760, 267, "Monthly gross sales - GBP",
           {"Category": [column("DimDate", "month")], "Y": [measure("Gross Merchandise Sales GBP")]},
           (field("DimDate", "month"), "Ascending"))
    visual(p, "ABCSales", "barChart", 802, 288, 454, 267, "ABC sales contribution - fixed full-period classes",
           {"Category": [column("DimSKU", "abc_class")], "Y": [measure("ABC Share of Sales")]},
           (field("DimSKU", "abc_class"), "Ascending"))
    visual(p, "TopSKUs", "barChart", 24, 574, 760, 264,
           "Full-period top 10 SKUs - sales in current selection",
           {"Category": [column("DimSKU", "product_label")], "Y": [measure("Top Ten SKU Sales GBP")]},
           (field("FactTransactions", "Top Ten SKU Sales GBP", True), "Descending"))
    textbox(p, "ManagementActions",
        "MANAGEMENT REVIEW\n825 A-class SKUs contribute 80.02% of full-period gross sales.\n"
        "Investigate SKU 23166: same-day opposite 74,215-unit entries.\n"
        "Validate observed stock and supplier data before ordering.\n"
        "Gross sales are before credits; no profit or savings claim.",
        802, 574, 454, 264, 13)
    textbox(p, "Footer", "Public UCI Online Retail | CC BY 4.0 | Stock scenarios are shown separately on page 3.", 24, 850, 1232, 34, 10, MUTED)

    p = "SKUPerformance"
    textbox(p, "Header", "SKU PERFORMANCE & CREDIT REVIEW", 24, 16, 1232, 70, 25, "#FFFFFF", NAVY)
    textbox(p, "Scope", "Observed sales and credits | ABC labels use the full twelve-month, all-country baseline.", 24, 94, 1232, 35, 12, MUTED)
    for name, table, prop, title, x, w in [
        ("SKUSlicer", "DimSKU", "product_label", "Product", 24, 570),
        ("ABCSlicer", "DimSKU", "abc_class", "ABC", 612, 130),
        ("MonthSlicer", "DimDate", "month", "Sales month", 760, 180),
        ("CountrySlicer", "FactTransactions", "country", "Country", 958, 298)]:
        visual(p, name, "slicer", x, 139, w, 60, title, {"Values": [column(table, prop)]})
    visual(p, "SKUDetail", "tableEx", 24, 218, 800, 615, "Product sales and credits",
        {"Values": [column("DimSKU", "sku", "SKU"), column("DimSKU", "description", "Product"),
            column("DimSKU", "abc_class", "ABC"), measure("Gross Units", "Units"),
            measure("Gross Merchandise Sales GBP", "Gross sales GBP"),
            measure("Cancellation Value GBP", "Credits GBP"),
            measure("Signed Transaction Value GBP", "Signed value GBP")]},
        (field("FactTransactions", "Gross Merchandise Sales GBP", True), "Descending"))
    visual(p, "VolumeLeaders", "barChart", 844, 218, 412, 370, "Top units - current selection",
        {"Category": [column("DimSKU", "sku")], "Y": [measure("Top Ten SKU Units")]},
        (field("FactTransactions", "Top Ten SKU Units", True), "Descending"))
    textbox(p, "CreditNote", "DATA QUALITY REVIEW\nSKU 23166 has 77,826 gross units and 74,494 credited units across the full period.\n"
        "A same-day match is an offset candidate, not a confirmed linked return.\n"
        "Preserve both signs and investigate original records before treating exceptional volume as recurring demand.",
        844, 608, 412, 225, 13)
    textbox(p, "Footer", "Historical filters apply to transaction measures. Fixed inventory assumptions are on page 3.", 24, 850, 1232, 34, 10, MUTED)

    p = "StockReviewScenario"
    textbox(p, "Header", "STOCK REVIEW - SYNTHETIC SCENARIO", 24, 16, 1232, 70, 25, "#FFFFFF", NAVY)
    textbox(p, "ScenarioWarning",
        "ASSUMED STOCK AND LEAD TIMES | Snapshot 30 Nov 2011 | Fixed 90-day sales lookback.\n"
        "These are illustrative review candidates, not observed stockouts, overstock or realised savings.",
        24, 102, 1232, 62, 13, "#795112", "#FFF0D5")
    for name, table, prop, title, x, w in [
        ("ABCSlicer", "DimSKU", "abc_class", "ABC class", 24, 180),
        ("StatusSlicer", "InventoryScenario", "scenario_flag", "Review status", 222, 300),
        ("ProductSlicer", "DimSKU", "product_label", "Product", 540, 716)]:
        visual(p, name, "slicer", x, 181, w, 55, title, {"Values": [column(table, prop)]})
    for i, (name, title) in enumerate([
        ("Scenario SKUs Due Reorder Review", "Reorder review"),
        ("Scenario SKUs Excess Cover Review", "Excess cover review"),
        ("Scenario SKUs Manual Review", "Manual demand review")]):
        visual(p, "ScenarioKPI" + str(i), "card", 24 + 418*i, 254, 396, 105, title,
            {"Values": [measure(name)]}, objects=card_options)
    visual(p, "ScenarioQueue", "tableEx", 24, 379, 1232, 363, "Illustrative stock policy review queue",
        {"Values": [column("DimSKU", "sku", "SKU"), column("DimSKU", "abc_class", "ABC"),
            column("InventoryScenario", "scenario_flag", "Review status"),
            column("InventoryScenario", "demand_status", "Demand screen"),
            column("InventoryScenario", "on_hand_units", "On hand"),
            column("InventoryScenario", "inventory_position_units", "Position"),
            column("InventoryScenario", "reorder_point_units", "Reorder point"),
            column("InventoryScenario", "suggested_order_units", "Suggested units"),
            column("InventoryScenario", "days_cover", "Days cover")]})
    textbox(p, "Actions",
        "REVIEW BEFORE ACTION\nPrioritise A-class candidates. Obtain observed balances, receipts, lead times and purchasing constraints.\n"
        "Manual-review products have blank suggested quantities. Their demand history is unsuitable for this baseline.\n"
        "Date and country filters do not recalculate the stored scenario. No historical date/country slicers are provided here.",
        24, 762, 1232, 100, 12)
    textbox(p, "Footer", "All balances, reservations, open orders and lead times are SYNTHETIC_SCENARIO inputs.", 24, 866, 1232, 34, 9, MUTED)
    write(PBI / "InventoryPalette.json", {"name": "Inventory Portfolio",
        "dataColors": [TEAL, "#4E7192", "#C7933D", "#83949F", "#9CBDB4", "#9A79A0"],
        "background": "#F3F6F8", "foreground": INK, "tableAccent": TEAL})


def main():
    schema, measures = build_model()
    build_report()
    visuals = list(REPORT.glob("definition/pages/*/visuals/*/visual.json"))
    print(json.dumps({"status": "AUTHORED", "tables": len(schema), "relationships": 3,
        "measures": len(measures), "pages": 3, "visuals": len(visuals),
        "desktop_execution": "PENDING_WINDOWS_CONFIRMATION"}, indent=2))


if __name__ == "__main__":
    main()
