# Data Dictionary

Source: RBI Database on Indian Economy, *Payment System Indicators* (monthly), file
`data/raw/rbi_payment_indicators_monthly.xlsx`. 82 months (Nov 2019 to Aug 2026), 70 indicators,
two measures per indicator (volume and value).

## Units (read from the sheet headers and verified by check V02)

| Measure | Unit in the sheet | Meaning |
|---|---|---|
| volume | `Volume (Lakh)` | 1 lakh = 100,000 transactions (for the *infrastructure* section it is a count of cards, ATMs, terminals, QR codes) |
| value | `Value( Rupees Crores )` | 1 crore = 10,000,000 rupees |

Average transaction value in rupees = `value_crore * 100 / volume_lakh` (because 1 crore / 1 lakh = 100).

## Sections and `kpi_scope`

| Source section | kpi_scope | Used for |
|---|---|---|
| A. Settlement Systems (CCIL) | `settlement` | Securities, forex and derivatives clearing |
| B. Payment Systems (RTGS, retail, cards, PPI, paper) | `payment_system` | **Main KPIs.** Additive: groups add up to the totals |
| A. Other Payment Channels, B. ATMs | `channel_view` | Mobile, internet, ATM views. **Overlap** with payment_system rows; never add them to totals |
| Payment System Infrastructures | `infrastructure` | Stock counts (cards issued, ATMs, PoS, QR). Their `value` cells are empty or zero in the RBI sheet and are not used |

## Hierarchy (`analysis_role`)

Codes such as `2.7.1` are only unique **inside a section**.

| analysis_role | hierarchy_level | Example |
|---|---|---|
| total | 0 | Total Payments (1+2+3+4+5+6) |
| group | 1 | 2 Credit Transfers - Retail |
| instrument | 2 | 2.7 UPI |
| sub_instrument | 3+ | 2.7.1 of which USSD |

`is_of_which = true` marks a subset of its parent (USSD is part of UPI); it is excluded when checking that
children add up to the parent. **Never sum different levels together: that double counts.**

## `data/cleaned/psi_monthly_long.csv` (one row per month x indicator x metric)

| Column | Type | Description |
|---|---|---|
| month_date | date | First day of the reporting month |
| section, sub_section | text | RBI section headings (`(none)` when the sheet has no sub-section) |
| indicator_code | text | Stable key: snake_case of the RBI header, first 60 characters |
| indicator_label | text | Header text exactly as in the sheet (whitespace collapsed) |
| code_number | text | RBI numbering such as `2.7` (empty for total rows) |
| indicator_name | text | Header without number and footnote symbols |
| footnote_marker | text | `@`, `$`, `*` as printed by RBI (new inclusion / separately initiated) |
| metric | text | `volume` or `value` |
| unit | text | `lakh` or `INR crore` |
| value | number | The reported figure |
| hierarchy_level, parent_code_number, parent_indicator_code | | Position in the hierarchy |
| analysis_role, kpi_scope | text | See tables above |
| is_of_which, has_children | bool | Hierarchy flags |
| display_order | int | Left-to-right order in the RBI sheet |
| is_zero, is_negative | bool | Value equals / is below zero (zeros are kept) |
| is_outlier | bool | Unusual month-on-month move (modified z-score above 6). A flag for review, nothing is removed |

## Other files in `data/cleaned/`

| File | Content |
|---|---|
| dim_indicator.csv | One row per indicator with all hierarchy attributes |
| rejected_rows.csv | Every sheet cell that did not become a row, with the reason |
| validation_report.csv | Result of every Python data-quality check |
| reconciliation_by_indicator.csv | Source vs processed vs database totals per indicator |
| vw_payment_kpi_monthly.csv | Month x indicator KPIs (growth, rolling average, share, rank) |
| vw_infrastructure_monthly.csv | Cards / ATMs / PoS / QR counts with growth |
| vw_kpi_headline.csv | One row per month for dashboard KPI cards |
| vw_fiscal_year_summary.csv | April-March fiscal-year totals and growth |
| vw_data_quality_latest.csv | Data-quality results of the last successful load |
| dim_date.csv | One row per month with calendar and fiscal-year columns |

## Database tables

| Table | Grain | Notes |
|---|---|---|
| etl_batch_log | one row per pipeline run | status, row counts, run time |
| stg_psi_long | cleaned long rows | fully reloaded each run |
| dim_indicator | one row per indicator | upserted on `indicator_code` |
| dim_date | one row per month | Indian fiscal year April-March |
| fact_payment_indicator | month x indicator | `volume_lakh` and `value_crore` side by side; primary key (month_date, indicator_id) |
| data_quality_log | one row per check per run | Python and SQL checks |

## Known source quirks

* RBI writes `-` where a figure is not available. Those cells become rows in `rejected_rows.csv`, never zeros.
* ECS Credit/Debit were merged into NACH from January 2020, so the ECS series stop or are sparse.
* Several indicators are new inclusions from Nov 2019 (`@`, `$`, `*` markers).
* The sheet header says the data are **provisional**; recent months can be revised.
* **Sep-2023:** the Prepaid Payment Instruments (group 5) *volume* is `-`, but the reported totals still include it.
  Total volume is therefore 4.65 percent above the sum of the published groups for that one month
  (implied missing amount 6,143.16 lakh). Values (INR crore) reconcile exactly in all 82 months.
