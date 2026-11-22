# Pipeline Run Summary

Generated automatically by the pipeline. Every number below was computed by the code,
not typed by hand. Re-run the pipeline to refresh it.

## 1. Ingest

| Metric | Value |
|---|---|
| source file | rbi_payment_indicators_monthly.xlsx |
| source sha256 | f0823d7734148acf8b4663dd03424879d344664aff0b3e1129bad630cac8e440 |
| source size kb | 135.4 |
| months found | 82 |
| first month | 2019-11-01 |
| last month | 2026-08-01 |
| data columns found | 140 |
| indicators found | 70 |
| raw rows in | 11,480 |
| numeric cells | 10,362 |
| dash placeholder cells | 1,118 |
| other non numeric cells | 0 |
| seconds | 0.489 |
| finished at | 2026-11-22T12:01:19 |

## 2. Clean

| Metric | Value |
|---|---|
| raw rows in | 11,480 |
| dash placeholder cells | 1,118 |
| other non numeric cells | 0 |
| duplicates removed | 0 |
| rejected by reason | {"interior_gap": 500, "leading_gap_not_yet_reported": 464, "trailing_gap_series_ended": 154} |
| rows rejected | 1,118 |
| rows after cleaning | 10,362 |
| zero values | 396 |
| negative values | 0 |
| outlier flags | 142 |
| indicators | 70 |
| months | 82 |
| date from | 2019-11-01 |
| date to | 2026-08-01 |
| nulls per column | {"code_number": 492, "parent_code_number": 3142, "parent_indicator_code": 3142} |
| seconds | 0.665 |
| role counts | {"instrument": 38, "group": 19, "sub_instrument": 10, "total": 3} |
| scope counts | {"payment_system": 35, "channel_view": 15, "infrastructure": 13, "settlement": 7} |
| finished at | 2026-11-22T12:01:20 |

## 3. Validate

| Metric | Value |
|---|---|
| checks run | 13 |
| passed | 10 |
| warnings | 2 |
| failed | 0 |
| info | 1 |
| seconds | 0.386 |
| finished at | 2026-11-22T12:01:20 |

## 4. Load to PostgreSQL

| Metric | Value |
|---|---|
| batch id | 1 |
| database | PostgreSQL 16.2 on x86_64-pc-linux-gnu |
| rows loaded staging | 10,362 |
| dim indicator rows | 70 |
| dim date rows | 82 |
| fact rows | 5,606 |
| sql checks passed | 10 |
| sql checks warn | 1 |
| sql checks failed | 0 |
| indicators reconciled | 70 |
| reconciliation mismatches | 0 |
| seconds | 3.99 |
| finished at | 2026-11-22T12:01:25 |

## 5. Power BI exports

| Metric | Value |
|---|---|
| vw payment kpi monthly rows | 4,550 |
| vw infrastructure monthly rows | 1,056 |
| vw kpi headline rows | 82 |
| vw fiscal year summary rows | 449 |
| vw data quality latest rows | 24 |
| dim indicator rows | 70 |
| dim date rows | 82 |
| seconds | 0.337 |
| finished at | 2026-11-22T12:01:26 |
