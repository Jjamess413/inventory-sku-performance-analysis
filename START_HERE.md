# Open the completed analysis

## James：今天完成 Power BI 的最后一步

三页报表、模型关系和 DAX 已经预置。先完成打开与核对，学习记录保留给之后继续。

**21 October 修正版：** 已修正报表内容版本，并补齐官方模板的元数据与主题文件。请将修正版完整解压到新文件夹，关闭之前的空白项目，再从新文件夹启动，避免混用旧文件。打开后先确认底部有三个页面标签，然后刷新数据。

1. **先解压下载的 ZIP。** 进入解压后的文件夹，确认能看到 `OPEN_POWERBI.cmd`、`powerbi` 和 `data`。
2. **双击 `OPEN_POWERBI.cmd`。** 它使用已经安装的 Python 3.13，把数据目录自动设置成当前文件夹，再打开 Power BI 项目。
3. 在 Power BI Desktop 中点击 **Refresh／刷新**，等待 CSV 导入完成。
4. 核对下面的全年控制数值，再检查三页报表。按 **Ctrl+S** 保存项目。

如果双击没有关联到 Power BI，在 Desktop 中选择 File → Open，打开 `powerbi/InventoryPortfolio.pbip`。数据路径仍由上面的启动脚本设置。

**21 October 核对结果：** James 已提供刷新后的第一页实际截图，四项控制数值全部吻合，三个页面标签及图表已显示。详见 [Desktop 记录](reports/powerbi_desktop_validation.json)。第三页数量与各页筛选交互仍可按下列预期继续核对。

| 第一页：不加筛选 | 预期值 |
| --- | ---: |
| Gross merchandise sales | £9,655,544.63 |
| Gross units | 5,263,714 |
| Sales orders | 18,957 |
| Active SKUs | 3,789 |

| 第三页：不加筛选，模拟库存 | 预期 SKU 数量 |
| --- | ---: |
| Reorder review | 984 |
| Excess cover review | 509 |
| Manual demand review | 1,845 |

第三页全部是明确标注的模拟库存与交期，不是实际缺货、积压或已实现降本。第一、二页的日期/国家筛选不应重新计算这个固定场景。

## View the browser dashboard immediately

Open `dashboard/index.html` in a browser. It works offline, including month/country filters, SKU search, pagination, product-level scenario details and CSV export. The browser dashboard is a separate deliverable from the native Power BI report.

## What is in the portable package?

| Location | Contents |
| --- | --- |
| `powerbi/InventoryPortfolio.pbip` | Native Power BI project entry point |
| `powerbi/InventoryPortfolio.Report/` | Three report pages and 34 visual containers |
| `powerbi/InventoryPortfolio.SemanticModel/` | Four-table import model, three relationships, 24 measures |
| `data/processed/` | Reviewed local CSV inputs and SQLite database; no source CustomerID column |
| `dashboard/index.html` | Completed standalone browser dashboard |
| `sql/` and `reports/` | Reproducible analytical questions, findings and validation evidence |

The public Git repository excludes raw workbooks, large transaction exports, local caches and PBIX files. Reproduce those inputs with `scripts/build.py` when using a fresh Git clone. The portable package supplies the reviewed local inputs for opening today.

## Reproduce from source

```bash
python -m pip install -r requirements.txt
python scripts/build.py
python -m unittest discover -s tests -v
python scripts/run_queries.py
python scripts/build_dashboard.py
python scripts/build_powerbi.py
python scripts/open_powerbi.py
```

Source: Chen, D. (2015), UCI Online Retail, [DOI 10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0. Sales are GBP and cover all included countries, 1 December 2010–30 November 2011.
