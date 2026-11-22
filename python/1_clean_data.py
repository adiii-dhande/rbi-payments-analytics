"""Step 1: read the RBI Excel sheet, clean it, check it, save one tidy CSV."""
import pandas as pd

RAW_FILE = "data/raw/rbi_payment_indicators_monthly.xlsx"
OUT_FILE = "data/cleaned/rbi_payments_clean.csv"

# ---- 1. Read the sheet (the header spans several rows) ----------------------
raw = pd.read_excel(RAW_FILE, header=None)
h = raw.index[raw[1] == "Month/Year"][0]            # row where the header starts
months = pd.to_datetime(raw[1], format="%b-%Y", errors="coerce")
rows = (months.notna()) & (raw.index > h)           # rows that hold monthly data

# header rows: section, indicator name, unit (Volume in lakh / Value in INR crore)
section = raw.iloc[h, 2:].ffill()
label = raw.iloc[h + 2, 2:].ffill()
unit = raw.iloc[h + 3, 2:]
keep_cols = unit.notna()                            # drop empty trailing columns

body = raw.loc[rows, raw.columns[2:]].loc[:, keep_cols.values]
body.index = months[rows].rename("month_date")
body = body.copy()
body.columns = range(body.shape[1])

meta = pd.DataFrame({"col": range(body.shape[1]),
                     "section": section[keep_cols].values,
                     "label": label[keep_cols].values,
                     "unit": unit[keep_cols].values})

# ---- 2. Wide -> long ---------------------------------------------------------
df = body.reset_index().melt(id_vars="month_date", var_name="col", value_name="value")
df = df.merge(meta, on="col").drop(columns="col")
cells_read = len(df)

# ---- 3. Clean ----------------------------------------------------------------
df["value"] = pd.to_numeric(df["value"], errors="coerce")   # RBI writes "-" when no figure -> NaN
dashes = int(df["value"].isna().sum())
df = df.dropna(subset=["value"])                             # a missing figure is not a zero

df["metric"] = df["unit"].str.contains("Volume").map({True: "volume_lakh", False: "value_crore"})
df["label"] = df["label"].str.split().str.join(" ")          # remove extra spaces
df["code"] = df["label"].str.extract(r"^(\d+(?:\.\d+)*)\s")[0].fillna("")
df["indicator"] = (df["label"].str.replace(r"^\d+(\.\d+)*\s+", "", regex=True)
                   .str.replace(r"[@$*#]", "", regex=True).str.split().str.join(" "))
df["level"] = df["code"].map(lambda c: 0 if c == "" else c.count(".") + 1)
# level 0 = RBI total rows, 1 = group (e.g. 2 Credit Transfers), 2 = instrument (e.g. 2.7 UPI), 3 = sub-item

# one row per month + indicator, with volume and value side by side
keys = ["month_date", "section", "code", "indicator", "level"]
clean = df.pivot_table(index=keys, columns="metric", values="value").reset_index()
clean.columns.name = None
clean = clean[keys + ["volume_lakh", "value_crore"]]
clean = clean.sort_values(["section", "code", "indicator", "month_date"]).reset_index(drop=True)
clean["month_date"] = clean["month_date"].dt.date

# ---- 4. Simple checks --------------------------------------------------------
print("Cells read from Excel      :", f"{cells_read:,}")
print("RBI '-' (no figure) removed:", f"{dashes:,}")
print("Figures kept               :", f"{len(df):,}")
print("Rows in clean table        :", f"{len(clean):,}")
print("Months / indicators        :", clean["month_date"].nunique(), "/", clean[["section", "code", "indicator"]].drop_duplicates().shape[0])
print("Date range                 :", clean["month_date"].min(), "to", clean["month_date"].max())
print("Duplicate rows             :", int(clean.duplicated(keys).sum()))
print("Negative values            :", int((clean[["volume_lakh", "value_crore"]] < 0).sum().sum()))

# Do the children add up to the parent? (group 2 should equal 2.1 + 2.2 + ... + 2.7)
pay = clean[clean["section"] == "B. Payment Systems"]
kids = pay[pay["level"] == 2].assign(code=lambda d: d["code"].str.split(".").str[0]) \
          .groupby(["month_date", "code"])[["volume_lakh", "value_crore"]].sum()
parents = pay[pay["level"] == 1].set_index(["month_date", "code"])[["volume_lakh", "value_crore"]]
diff = (parents - kids).abs() / parents.abs()
bad = (diff > 0.001).sum().sum()
print("Parent = sum of children   :", "OK" if bad == 0 else f"{bad} mismatches", f"({parents.notna().sum().sum()} comparisons)")

clean.to_csv(OUT_FILE, index=False)
print("Saved ->", OUT_FILE)
