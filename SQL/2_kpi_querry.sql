-- Q1. Latest month: payment instruments ranked by number of transactions
SELECT indicator, volume_lakh, value_crore,
       ROUND(value_crore * 100 / NULLIF(volume_lakh, 0), 2)  AS avg_transaction_inr,
       RANK() OVER (ORDER BY volume_lakh DESC)               AS volume_rank
FROM payment_indicators
WHERE section = 'B. Payment Systems' AND level = 2
  AND month_date = (SELECT MAX(month_date) FROM payment_indicators)
ORDER BY volume_rank;

-- Q2. Total payments per month (RBI total row)
SELECT month_date, volume_lakh AS total_volume_lakh, value_crore AS total_value_crore
FROM payment_indicators
WHERE section = 'B. Payment Systems' AND level = 0 AND indicator LIKE 'Total Payments%'
ORDER BY month_date;

-- Q3. UPI growth: month-on-month and year-on-year (LAG)
SELECT month_date, volume_lakh, value_crore,
       ROUND(100 * (volume_lakh / LAG(volume_lakh, 1)  OVER (ORDER BY month_date) - 1), 2) AS volume_mom_pct,
       ROUND(100 * (volume_lakh / LAG(volume_lakh, 12) OVER (ORDER BY month_date) - 1), 2) AS volume_yoy_pct,
       ROUND(100 * (value_crore / LAG(value_crore, 12) OVER (ORDER BY month_date) - 1), 2) AS value_yoy_pct
FROM payment_indicators
WHERE section = 'B. Payment Systems' AND code = '2.7'          -- 2.7 = UPI
ORDER BY month_date;

-- Q4. Channel contribution: each group's share of total payments, latest month
WITH latest AS (
    SELECT * FROM payment_indicators
    WHERE section = 'B. Payment Systems' AND month_date = (SELECT MAX(month_date) FROM payment_indicators)
)
SELECT g.code, g.indicator,
       ROUND(100 * g.volume_lakh / t.volume_lakh, 2) AS volume_share_pct,
       ROUND(100 * g.value_crore / t.value_crore, 2) AS value_share_pct
FROM latest g
JOIN latest t ON t.level = 0 AND t.indicator LIKE 'Total Payments%'
WHERE g.level = 1
ORDER BY value_share_pct DESC;

-- Q5. UPI 3-month rolling average of transactions (the first two months average fewer than 3 months)
SELECT month_date, volume_lakh,
       ROUND(AVG(volume_lakh) OVER (ORDER BY month_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg
FROM payment_indicators
WHERE section = 'B. Payment Systems' AND code = '2.7'
ORDER BY month_date;

-- Q6. Rank of retail credit-transfer channels (2.1 to 2.7) by value, latest month
SELECT indicator, value_crore,
       RANK() OVER (ORDER BY value_crore DESC) AS value_rank
FROM payment_indicators
WHERE section = 'B. Payment Systems' AND level = 2 AND code LIKE '2.%'
  AND month_date = (SELECT MAX(month_date) FROM payment_indicators)
ORDER BY value_rank;

-- Q7. Fiscal year (April to March) totals for UPI, NEFT, IMPS
--     FY2019-20 and the current year are partial: look at months_reported
SELECT CASE WHEN EXTRACT(MONTH FROM month_date) >= 4
            THEN 'FY' || EXTRACT(YEAR FROM month_date)::INT     || '-' || RIGHT((EXTRACT(YEAR FROM month_date)::INT + 1)::TEXT, 2)
            ELSE 'FY' || (EXTRACT(YEAR FROM month_date)::INT - 1) || '-' || RIGHT(EXTRACT(YEAR FROM month_date)::INT::TEXT, 2)
       END AS fiscal_year,
       indicator,
       COUNT(*)                   AS months_reported,
       ROUND(SUM(volume_lakh), 0) AS volume_lakh,
       ROUND(SUM(value_crore), 0) AS value_crore
FROM payment_indicators
WHERE section = 'B. Payment Systems' AND code IN ('2.4', '2.6', '2.7')   -- IMPS, NEFT, UPI
GROUP BY 1, indicator
ORDER BY 1, indicator;
