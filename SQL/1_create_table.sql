
DROP TABLE IF EXISTS payment_indicators;

CREATE TABLE payment_indicators (
    month_date   DATE          NOT NULL,
    section      TEXT          NOT NULL,
    code         TEXT          NOT NULL,      -- RBI numbering such as 2.7 (empty for total rows)
    indicator    TEXT          NOT NULL,
    level        SMALLINT      NOT NULL,
    volume_lakh  NUMERIC(24,6),
    value_crore  NUMERIC(24,6),
    PRIMARY KEY (month_date, section, code, indicator)
);
