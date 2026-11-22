# KPI Definitions

Units: volume in **lakh**, value in **INR crore**. 1 lakh = 100,000; 1 crore = 10,000,000.
All KPIs below are computed in SQL (`SQL/04_kpi_queries.sql` for analysis, `SQL/05_views_for_powerbi.sql` for the
reporting views). Growth figures are NULL when the comparison month does not exist or the base is zero.

| KPI | Definition | Where |
|---|---|---|
| Total transactions | `volume_lakh` of the indicator in the month. Use the RBI Total row or a single `analysis_role`; never sum levels | vw_payment_kpi_monthly |
| Total transaction value | `value_crore` of the indicator in the month | vw_payment_kpi_monthly |
| Average transaction value (INR) | `value_crore * 100 / volume_lakh` | all views |
| MoM growth % | `(this month / previous month - 1) * 100`, only if the previous calendar month exists | `volume_mom_pct`, `value_mom_pct` |
| YoY growth % | `(this month / same month last year - 1) * 100`, only if that month exists | `volume_yoy_pct`, `value_yoy_pct` |
| Rolling 3-month average | Average of the current and previous two months, only when all three exist | `rolling_3m_avg_*` |
| Channel contribution % | `indicator / Total Payments (1+2+3+4+5+6) * 100` in the same month, `payment_system` scope only | `share_of_total_payments_*_pct` |
| Rank of channels | `RANK()` within month, scope and analysis_role, by volume or by value | `rank_by_volume_in_role`, `rank_by_value_in_role` |
| Digital share % | `Total Digital Payments (1+2+3+4+5) / Total Payments` | vw_kpi_headline |
| UPI share of digital % | `UPI / Total Digital Payments` | vw_kpi_headline |
| Fiscal-year total | Sum of the 12 months April-March; `is_complete_fy` is false for partial years | vw_fiscal_year_summary |
| Fiscal-year YoY % | Only when both fiscal years are complete | `volume_fy_yoy_pct`, `value_fy_yoy_pct` |

## Cautions

* **"Digital" follows the RBI definition** (groups 1-5: RTGS, retail credit transfers, debit transfers, cards, PPI).
  RTGS and NEFT are therefore digital, so the digital share is close to 100 percent by volume.
* **Volume and value tell different stories.** In Aug 2026, RTGS is 0.11 percent of transactions but 68.49 percent of value;
  UPI is 86.98 percent of transactions but 9.92 percent of value (shares of Total Payments).
* **FY2019-20 and FY2026-27 are partial** (5 months each), so they are not comparable with full years.
* **Sep-2023 volume totals** are 4.65 percent above the sum of their groups because PPI volume is blank in the source.
* Channel-view rows (mobile, internet, ATM) overlap with other instruments, so no share-of-total is computed for them.
