# Data Quality Rules

Every rule runs automatically. Results are written to `data/cleaned/validation_report.csv`, loaded into the
`data_quality_log` table and shown by `vw_data_quality_latest`.

Status meaning: **PASS** rule holds, **WARN** a real property of the source data that you should know about
(data is kept as published), **FAIL** the pipeline is wrong or the source is unusable (the run stops with exit code 1),
**INFO** counted for review only.

## Python checks (step 3)

| ID | Rule | Why it matters |
|---|---|---|
| V01 | Two metric columns per indicator; indicator keys are unique | Detects a changed sheet layout or key collisions |
| V02 | Unit headers are `Volume (Lakh)` and `Value( Rupees Crores )` in every column | Wrong units would silently ruin averages and growth |
| V03 | Months parse and run continuously with no missing month | Growth (MoM, YoY) needs consecutive months |
| V04 | Every cell is a number or RBI's `-` placeholder | Catches stray text such as notes or typos |
| V05 | No duplicate (month, indicator, metric) | Duplicates inflate every total |
| V06 | Empty cells are explained: leading, trailing or interior gap | Interior gaps are suspicious (WARN) |
| V07 | No negative values; zeros are kept and counted | Zeros are real in discontinued series |
| V08 | Parent equals the sum of its children (excluding "of which") for every parent, both measures, every month, tolerance 0.1 percent | Proves the hierarchy is additive before KPIs use it |
| V09 | The three RBI total rows equal the sum of their groups | Proves Total Payments can be used as a denominator |
| V10 | Source (Excel) totals equal processed totals for every indicator and metric | Nothing lost or altered in cleaning |
| V11 | Row accounting: raw cells = cleaned rows + rejected rows | No row disappears silently |
| V12 | Cleaned data equals the earlier `psi_monthly_long.csv` extract | Independent cross-check of the parser |
| V13 | Unusual month-on-month moves are flagged | Review list (e.g. the April-May 2020 lockdown) |

## SQL checks (step 4, file `SQL/03_data_quality_checks.sql`)

| ID | Rule |
|---|---|
| S01 | dim_indicator rows = distinct indicators in staging |
| S02 | dim_date covers every month, no gaps |
| S03 | fact rows = distinct (month, indicator) pairs |
| S04 | non-null fact measures = staging rows |
| S05, S06 | sum of value / volume: staging equals fact (integrity only, not a KPI) |
| S07 | no orphan fact rows |
| S08 | negative values and zero values counted |
| S09, S10 | Total Payments value / volume equals the sum of its six groups in every month |
| S11 | Latest UPI average ticket is plausible (INR 10 to 100,000) |

## Reconciliation

`reconciliation_by_indicator.csv` compares, for each of the 70 indicators and both measures, the total in the Excel
source, in the cleaned CSV and in PostgreSQL. A row is `MATCH` when the largest difference is at most 0.001.
