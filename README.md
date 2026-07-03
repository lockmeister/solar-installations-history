# NZ solar installations history

Public snapshot archive for Electricity Authority NZ solar installation CSV datasets.

Source dataset page: https://www.ea.govt.nz/data-and-insights/datasets/Datasets/Retail/SolarInstallations/

Files tracked:
- `SolarInstallationsByStreet.csv`
- `SolarInstallationsByRegion.csv`

Schedule: weekly GitHub Actions run. The action downloads the current public CSVs, writes `data/current/`, stores dated snapshots under `data/snapshots/YYYY-MM-DD/`, updates `metadata/manifest.jsonl`, and commits only when content changes.

Notes:
- EA publishes current CSV files; this repository preserves public history via git commits and dated snapshots.
- `SolarInstallationsByStreet.csv` is the stable data source for the local solar map work. It has street/SA2/market-segment/count/kW fields, but no coordinates. Existing map code using Sigma-captured GeoJSON coordinates needs a separate geography join or a one-off coordinate reference.
- `shot-scraper` is not used: this is CSV archival, not webpage screenshotting.
