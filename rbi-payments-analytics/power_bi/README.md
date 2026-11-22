# Power BI (next step)

The dashboard is not built yet. Everything it needs is ready.

## Import these files (Get Data > Text/CSV) from `data/cleaned/`

| File | Use |
|---|---|
| vw_kpi_headline.csv | KPI cards and the overview trend |
| vw_payment_kpi_monthly.csv | Channel comparison, growth, share, rank |
| vw_fiscal_year_summary.csv | Fiscal-year view |
| vw_infrastructure_monthly.csv | Cards, ATMs, PoS, QR counts |
| dim_date.csv, dim_indicator.csv | Dimensions for slicers |

## Model

* `dim_date[month_date]` 1 to many `vw_payment_kpi_monthly[month_date]` and `vw_kpi_headline[month_date]`.
* `dim_indicator[indicator_code]` 1 to many `vw_payment_kpi_monthly[indicator_code]`.
* Filter every channel visual with `analysis_role = "instrument"` (or `"group"`) and `kpi_scope = "payment_system"`.
  Never sum across roles: that double counts (see `documentation/data_dictionary.md`).
* Units: volume in lakh, value in INR crore. Label axes accordingly.
