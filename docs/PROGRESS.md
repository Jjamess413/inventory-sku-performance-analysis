# Progress and next-session handover

Last updated: 19 October 2026. Project owner: James You.

## Status

The SQL analysis foundation is implemented and validated. The Power BI dashboard, owner learning checks and final career presentation are not complete. This project is publicly labelled in development and should not yet be pinned as a finished portfolio piece.

The initial code and documentation were developed with AI-assisted scaffolding. Independent explanation, hands-on modifications and Desktop validation are explicit release requirements.

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
- [x] James opens the generated database in DB Browser for SQLite and executes the supplied top-five sales query. All five rows in the owner-provided result screenshot match the reference results. This confirms guided execution; independently modified SQL and an explanation are still pending.

## Next actions

- [ ] Run the 10 business-rule unit tests and saved-query runner on James's Windows environment; review the actual output.
- [ ] James modifies the starter query to rank the ten highest-volume SKUs and explains `GROUP BY sku`.
- [ ] James runs and explains the November SQL exercise in `learning_exercises.md`.
- [ ] Review the answer and update the learning log with actual feedback.
- [ ] Confirm James's local Power BI environment and guide the first import.
- [ ] Build the star schema and reconcile the first two measures in Desktop.
- [ ] Complete the three report pages, test interactions and save the actual PBIX.
- [ ] Capture actual Power BI screenshots and check them for clear source/scenario labels.
- [ ] Explain a SKU recommendation and the cancellation anomaly independently.
- [ ] Review for release; then pin the completed project and prepare LinkedIn Featured copy, resume bullets and English interview pitches.

## Continuity instructions

Use this repository's current default branch as the source of truth. Read this file, the README and `reports/validation.json` at the beginning of a later session. Inspect existing files before editing them. Do not recreate the repository or overwrite owner learning notes.

Rebuild the analysis only after a source/configuration/code change or a failed validation. Checksum changes require provenance review. Update findings and control totals when calculations change. Do not publish private employer or e-commerce data to complete a missing input.

The existing `ibm` repository is retained as earlier learning work. The two existing private projects remain outside this portfolio. No deletion or visibility change is part of this plan.
