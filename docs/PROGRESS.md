# Progress and next-session handover

Last updated: 21 October 2026. Project owner: James You.

## Status

The SQL/Python analysis and standalone browser dashboard are complete and validated. The native Power BI project has four tables, three relationships, 24 measures and three pages/34 visual containers. Its public JSON structures and field references pass validation. On 21 October James supplied an actual Windows Desktop screenshot after refresh: the executive overview's four control totals match the SQL reference and its charts and three page tabs are visible. Other native page and slicer checks remain in reports/powerbi_desktop_validation.json.

On 21 October James explicitly requested delivery today and deferred further learning. The earlier owner-explanation gate is therefore postponed, not reported as completed. The implementation is AI-assisted. Learning notes remain preserved and are separate from artefact acceptance. James subsequently confirmed the delivered report and explicitly authorised publication to GitHub. Native validation claims are limited to the recorded screenshot evidence.

## Delivery work completed on 21 October

The initial package's blank Desktop canvas was resolved by correcting the PBIR content version and adding the scaffolded platform/theme resources. The corrected shell follows Microsoft report-authoring CLI 0.5.0, passes its offline validation with no diagnostics, and adds explicit version/page/resource guards. Subsequent owner screenshots confirm that the three pages load and the refreshed executive overview reconciles.

- [x] Preserve the original checkout and owner notes; implement in an isolated worktree from the current remote main branch.
- [x] Rerun the ten meaningful business-rule tests and the saved business queries successfully.
- [x] Add full-period monthly sales/units comparison SQL and export; November growth is 31.72% sales and 20.64% units.
- [x] Build the standalone interactive browser dashboard from 62,679 SKU/month/country aggregates.
- [x] Reconcile eleven dashboard data checks, including order grain and blank manual-review recommendations.
- [x] Pass fifteen Chromium runtime checks covering filters, search, sort, paging, details, export, mobile width and errors.
- [x] Capture actual browser overview, SKU and scenario pages, labelled separately from Power BI screenshots.
- [x] Author the native PBIP/PBIR report and TMSL import model; validate public schemas and field references.
- [x] Prepare an automatic local-path launcher, opening instructions, business case and career presentation notes.
- [x] Confirm actual Windows Power BI Desktop overview refresh, four control totals, rendered charts and visible page tabs; retain the owner's screenshot.
- [ ] Review the other native pages and slicer interactions in detail.

## Completed

- [x] Check existing GitHub repositories and profile before creating new content.
- [x] Preserve existing projects and their visibility.
- [x] Set profile name, positioning, Sydney location and LinkedIn link.
- [x] Create the profile README with honest skills and project statuses.
- [x] Create the inventory repository and its description/topics.
- [x] Compare public dataset options and verify the selected UCI source and licence.
- [x] Download the complete source workbook and verify its checksum.
- [x] Implement transaction classification, explicit exclusions and repeat-row policy.
- [x] Keep customer IDs out of model exports and public reports.
- [x] Build SQL dimensions, facts, ABC, daily demand and labelled stock scenarios.
- [x] Execute the pipeline, meaningful business-rule tests and saved business queries.
- [x] Record actual findings, review candidates, assumptions and validation evidence.
- [x] Prepare Power Query starters, DAX and the Desktop build/reconciliation guide.
- [x] James extracts the project ZIP, creates a local Python environment and completes the first Windows build. The owner-provided terminal screenshot shows Python 3.13.16, pandas 3.0.6, PASS on 14 pipeline checks, 511,035 model rows and 3,789 model SKUs. Windows unit tests and saved-query runner output remain to be reviewed.
- [x] James opens the generated database in DB Browser for SQLite and executes the supplied top-five sales query. All five rows in the owner-provided result screenshot match the reference results. This confirms guided execution; the subsequent modified-query review is recorded below.
- [x] Review James's first modified SQL submission and grouping explanation. The ten-row descending-volume result matches the reference. The requested secondary SKU sort is verified in his subsequent October query, including an actual 3,320-unit tie.
- [x] Verify execution of the guided October date-filter example.
- [x] Review the owner's November WHERE/HAVING modification and basic row-versus-group explanation. The corrected 5,000-unit query returns seven matching rows. Whole-query authorship without a scaffold has not been assessed.

- [x] Verify the owner's product-description INNER JOIN result and `AS product_name` modification. All seven SKU quantities and sales values reconcile with the pre-join November result. A fuller independent matching-key and row-preservation explanation remains pending.

- [x] Review the owner's duplicate-match thought exercise: two matches for one 10-unit line yield two rows and a sum of 20. This is a teaching scenario.
- [x] Record the owner's reported zero-row LEFT JOIN missing-product result, consistent with the mentor's model check. Clarify that LEFT JOIN preserves rows; the owner's corrected explanation remains to be reviewed.

- [x] Review the owner's reported CASE threshold outcome: SKU 22086 becomes High volume at a 7,000-unit threshold because its November sales are 7,908. This verifies the threshold reasoning against the mentor reference; independent CASE authorship and condition-order explanation remain unassessed.

## Next actions

1. Publish the owner's authorised project update, including the actual native overview capture and its evidence record.
2. Review other native pages and slicer behaviour when continuing validation; preserve the recorded scope of the overview confirmation.
3. Publish/pin career material with the appropriate completed-component status. Keep native and browser captures labelled by their origin.
4. Resume independent SQL/DAX/model explanation later, as James requested. Historical learning checks and original submissions remain in learning_log.md.

## Continuity instructions

Use this repository's current default branch as the source of truth. Read this file, the README and `reports/validation.json` at the beginning of a later session. Inspect existing files before editing them. Do not recreate the repository or overwrite owner learning notes.

Rebuild the analysis only after a source/configuration/code change or a failed validation. Checksum changes require provenance review. Update findings and control totals when calculations change. Do not publish private employer or e-commerce data to complete a missing input.

The existing `ibm` repository is retained as earlier learning work. The two existing private projects remain outside this portfolio. No deletion or visibility change is part of this plan.
