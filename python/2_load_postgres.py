"""Step 2: create the table in PostgreSQL and load the clean CSV."""
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
url = (f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', '')}"
       f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'rbi_payments')}")
engine = create_engine(os.getenv("DATABASE_URL", url))

df = pd.read_csv("data/cleaned/rbi_payments_clean.csv", dtype={"code": str}, keep_default_na=False,
                 na_values=[""]).fillna({"code": ""})

with engine.begin() as conn:
    conn.exec_driver_sql(open("SQL/1_create_table.sql").read())      # drops and recreates payment_indicators
    df.to_sql("payment_indicators", conn, if_exists="append", index=False)
    rows = conn.execute(text("SELECT count(*) FROM payment_indicators")).scalar_one()
    months = conn.execute(text("SELECT count(DISTINCT month_date) FROM payment_indicators")).scalar_one()

print("Rows in CSV         :", f"{len(df):,}")
print("Rows in PostgreSQL  :", f"{rows:,}", "->", "OK" if rows == len(df) else "MISMATCH")
print("Months in PostgreSQL:", months)
