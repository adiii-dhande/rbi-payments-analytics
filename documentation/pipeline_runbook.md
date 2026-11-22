# Pipeline Runbook

## What each step does

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 Ingest | `python/01_ingest.py` | `data/raw/rbi_payment_indicators_monthly.xlsx` | `data/interim/raw_long.csv`, `header_meta.csv` |
| 2 Clean | `python/02_clean.py` | interim files | `data/cleaned/psi_monthly_long.csv`, `dim_indicator.csv`, `rejected_rows.csv` |
| 3 Validate | `python/03_validate.py` | raw + cleaned files | `data/cleaned/validation_report.csv` |
| 4 Load | `python/04_load_postgres.py` | cleaned CSV, `SQL/01`-`03` | tables in `rbi_payments`, `reconciliation_by_indicator.csv` |
| 5 Export | `python/05_export_powerbi.py` | `SQL/05` views | `data/cleaned/vw_*.csv`, `dim_date.csv` |

`python python/run_pipeline.py` runs them in order and stops at the first failure.
`--skip-db` runs steps 1-3 only (no PostgreSQL needed). `--reset-db` drops and recreates the project tables first.
Every step is safe to repeat: the load upserts, so running it twice never duplicates rows.

## Updating with new RBI data

1. Download the latest *Payment System Indicators* monthly sheet from data.rbi.org.in.
2. Save it over `data/raw/rbi_payment_indicators_monthly.xlsx` (keep the same file name).
3. Run `python python/run_pipeline.py`. Check the validation summary: a FAIL means the layout or units changed.
4. RBI marks recent months provisional, so earlier months can change; the load replaces facts that were revised.

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| `pip install psycopg2-binary` fails | Use Python 3.11 or 3.12 (64-bit) and `python -m pip install --upgrade pip`. Do not install plain `psycopg2`. |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. |
| `Cannot connect to PostgreSQL` | PostgreSQL service not running, wrong port, or wrong values in `.env`. Check with pgAdmin using the same values. |
| `password authentication failed` | `DB_PASSWORD` in `.env` differs from your postgres password. Avoid spaces around `=`. |
| `database "rbi_payments" does not exist` | In pgAdmin run `CREATE DATABASE rbi_payments;`, then rerun step 4. |
| `relation ... does not exist` or `column ... does not exist` | Tables from an earlier attempt have another structure. Run `python python/04_load_postgres.py --reset` (drops the project tables and recreates them). |
| Step 1 says the source file is missing | The Excel file must be at `data/raw/rbi_payment_indicators_monthly.xlsx`. |
| Step 1 says `Header row 'Month/Year' not found` | RBI changed the sheet layout. Open the file and compare it with the original. |
| Dates fail to parse (V03 fails) | Month labels such as `Aug-2026` need English month names. Check the Windows region/language settings. |
| Garbled characters in a CSV | Files are UTF-8. In Excel use Data > From Text/CSV and choose UTF-8; Power BI reads them correctly. |
| V02 fails (units) | RBI changed the unit text. Confirm the new units in the sheet before trusting any KPI, then update `EXPECTED_UNITS` in `python/config.py`. |
| Averages look 100x wrong | Units mixed. Average ticket in rupees is `value_crore * 100 / volume_lakh`. |
