import sqlite3
import pandas as pd
import os

# -------------------------------------------------------
# Create output folder
# -------------------------------------------------------

os.makedirs("output", exist_ok=True)

# -------------------------------------------------------
# Connect Database
# -------------------------------------------------------

conn = sqlite3.connect("nifty100.db")

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

market = pd.read_sql(
    "SELECT * FROM market_cap_clean",
    conn
)

companies = pd.read_sql(
    "SELECT * FROM companies_clean",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors_clean",
    conn
)

conn.close()

# -------------------------------------------------------
# Latest Market Cap record for each company
# -------------------------------------------------------

market = (
    market
    .sort_values("year")
    .drop_duplicates(
        subset="company_id",
        keep="last"
    )
)

# -------------------------------------------------------
# Merge all tables
# -------------------------------------------------------

df = ratios.merge(
    market,
    on="company_id",
    how="left"
)

df = df.merge(
    sectors,
    on="company_id",
    how="left"
)

df = df.merge(
    companies,
    on="company_id",
    how="left"
)

# -------------------------------------------------------
# FCF Yield
# -------------------------------------------------------

df["FCF_yield_pct"] = (
    df["free_cash_flow_cr"] /
    df["market_cap_crore"]
) * 100

# Avoid divide by zero
df["FCF_yield_pct"] = df["FCF_yield_pct"].fillna(0)

# -------------------------------------------------------
# Latest financial ratio record
# -------------------------------------------------------

latest = (
    df
    .sort_values("year_x")
    .drop_duplicates(
        subset="company_id",
        keep="last"
    )
)

# -------------------------------------------------------
# Sector Median PE
# -------------------------------------------------------

sector_median = (
    latest
    .groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_median.rename(
    columns={
        "pe_ratio": "sector_median_pe"
    },
    inplace=True
)

latest = latest.merge(
    sector_median,
    on="broad_sector",
    how="left"
)

# -------------------------------------------------------
# PE vs Sector Median
# -------------------------------------------------------

latest["PE_vs_sector_median_pct"] = (
    latest["pe_ratio"] /
    latest["sector_median_pe"]
) * 100

# -------------------------------------------------------
# Valuation Flag
# -------------------------------------------------------

def valuation_flag(row):

    pe = row["pe_ratio"]
    median = row["sector_median_pe"]

    if pd.isna(pe) or pd.isna(median):
        return "Fair"

    if pe > median * 1.5:
        return "Caution"

    elif pe < median * 0.7:
        return "Discount"

    else:
        return "Fair"


latest["flag"] = latest.apply(
    valuation_flag,
    axis=1
)

# -------------------------------------------------------
# Final Output
# -------------------------------------------------------

valuation = latest[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "sector_median_pe",
        "PE_vs_sector_median_pct",
        "flag"
    ]
].copy()

valuation.columns = [
    "company_id",
    "company_name",
    "sector",
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "5yr_median_PE",
    "PE_vs_sector_median_pct",
    "flag"
]

# -------------------------------------------------------
# Save Outputs
# -------------------------------------------------------

valuation.to_excel(
    "output/valuation_summary.xlsx",
    index=False
)

valuation[
    valuation["flag"] != "Fair"
].to_csv(
    "output/valuation_flags.csv",
    index=False
)

# -------------------------------------------------------
# Summary
# -------------------------------------------------------

print("=" * 50)
print("Valuation Module Completed")
print("Companies Processed :", len(valuation))
print(
    "Companies Flagged  :",
    len(valuation[valuation["flag"] != "Fair"])
)
print("Output : output/valuation_summary.xlsx")
print("Output : output/valuation_flags.csv")
print("=" * 50)