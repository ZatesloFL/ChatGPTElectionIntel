# 2026 Election Intelligence Dashboard

Public, evidence-first election monitoring dashboard. The initial snapshot is explicitly incomplete; no model probabilities or polling data have been fabricated.

## Publish
In repository Settings → Pages, select **GitHub Actions** as the build source. The `Publish dashboard` workflow deploys on pushes to main and can be run manually.

## Daily updates
The ChatGPT daily research reminder is **not** connected to this repository. The publishing workflow redeploys committed changes, but does not independently collect election data. To automate verified daily data ingestion, implement a separate bounded collector with provenance and validation, then commit a new snapshot and report.

## Data contract
`data/latest.json` is a status-only placeholder until verified observations exist. Do not replace missing values with zeros. Preserve source URLs, retrieved timestamps, candidate verification and freshness flags for each published observation.

## Word reports
Place reviewed .docx exports in `reports/` and link them from the dashboard after upload.
