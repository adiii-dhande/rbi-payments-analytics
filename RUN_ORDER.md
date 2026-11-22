# Run Order (Windows PowerShell)

Take every screenshot at full window size and save it in the project's `screenshots/` folder with the exact file name shown.
"Expect" shows what a correct run prints, so you can tell at a glance that it worked.

| # | Do this | Expect | Screenshot file name | Save in |
|---|---|---|---|---|
| 0 | `cd` into the project folder, then `py -3.11 -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `python -m pip install -r requirements.txt` | `Successfully installed ...` | `00-setup-install.png` | `screenshots/` |
| 1 | `Copy-Item .env.example .env`, edit `.env` with your postgres password. In pgAdmin run `CREATE DATABASE rbi_payments;` (skip if it exists) | database visible in pgAdmin tree | `01-pgadmin-database.png` | `screenshots/` |
| 2 | `python -m pytest` | `10 passed` | `02-tests-passed.png` | `screenshots/` |
| 3 | `python python/01_ingest.py` | `months_found 82`, `indicators_found 70`, `raw_rows_in 11480`, `numeric_cells 10362`, `dash_placeholder_cells 1118` | `03-ingest.png` | `screenshots/` |
| 4 | `python python/02_clean.py` | `rows_after_cleaning 10362`, `rows_rejected 1118`, `duplicates_removed 0` | `04-clean.png` | `screenshots/` |
| 5 | `python python/03_validate.py` | `Validation: 10 passed, 2 warnings, 0 failed, 1 info (13 checks)` | `05-validation.png` | `screenshots/` |
| 6 | `python python/04_load_postgres.py --reset` | `dim_indicator=70 dim_date=82 fact_payment_indicator=5606`, `70 of 70 indicators match, 0 mismatches` | `06-load-postgres.png` | `screenshots/` |
| 7 | pgAdmin: refresh the database, expand Schemas > public > Tables | 6 tables: etl_batch_log, stg_psi_long, dim_indicator, dim_date, fact_payment_indicator, data_quality_log | `07-pgadmin-tables.png` | `screenshots/` |
| 8 | pgAdmin Query Tool: open `SQL/03_data_quality_checks.sql`, press F5 | 11 rows; S10 is WARN (Sep-2023), the rest PASS | `08-sql-quality-checks.png` | `screenshots/` |
| 9 | `python python/05_export_powerbi.py` | 7 CSV files written, `vw_kpi_headline 82 rows` | `09-export-csvs.png` | `screenshots/` |
| 10 | pgAdmin: open `SQL/04_kpi_queries.sql`, select the text of **Q1** only, press F5 | 17 rows, UPI ranked first | `10-kpi-q1-snapshot.png` | `screenshots/` |
| 11 | Same for **Q3** | 82 rows, UPI MoM and YoY growth columns | `11-kpi-q3-upi-growth.png` | `screenshots/` |
| 12 | Same for **Q4** | 6 rows, RTGS about 68 percent of value but about 0.1 percent of volume | `12-kpi-q4-channel-share.png` | `screenshots/` |
| 13 | pgAdmin: Schemas > public > Views | 5 views starting with `vw_` | `13-pgadmin-views.png` | `screenshots/` |
| 14 | File Explorer: open `data/cleaned/` | 11 CSV files | `14-cleaned-folder.png` | `screenshots/` |
| 15 | `python python/run_pipeline.py` (full run, proves it is repeatable) | `Pipeline finished`, still `fact_payment_indicator=5606` | `15-full-pipeline.png` | `screenshots/` |
| 16 | Follow `PUSH_TO_GITHUB.md`, then open the repo on github.com | files visible | `16-github-repo.png` | `screenshots/` |

Notes
* Steps 3-6 are also done by `python python/run_pipeline.py --reset-db` in one go.
* Only the PostgreSQL step and the exports need your database; steps 3-5 work without it (`run_pipeline.py --skip-db`).
* Timings differ per machine; row counts must match exactly. If a number differs, stop and check `documentation/pipeline_runbook.md`.
