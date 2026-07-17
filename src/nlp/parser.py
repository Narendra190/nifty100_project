import sqlite3
import pandas as pd
import re
import os

os.makedirs("output", exist_ok=True)

# ---------------------------------------
# Connect Database
# ---------------------------------------

conn = sqlite3.connect("nifty100.db")

analysis = pd.read_sql(
    "SELECT * FROM analysis_clean",
    conn
)

ratios = pd.read_sql(
    """
    SELECT company_id,
           revenue_cagr_5yr,
           pat_cagr_5yr
    FROM financial_ratios
    """,
    conn
)

conn.close()

# ---------------------------------------
# Regex Pattern
# ---------------------------------------

pattern = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%")

fields = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]

parsed_rows = []
failed_rows = []

# ---------------------------------------
# Parse Text
# ---------------------------------------

for _, row in analysis.iterrows():

    company = row["company_id"]

    for field in fields:

        value = row[field]

        if pd.isna(value):
            continue

        matches = pattern.findall(str(value))

        if matches:

            for period, pct in matches:

                parsed_rows.append({
                    "company_id": company,
                    "metric_type": field,
                    "period_years": int(period),
                    "value_pct": float(pct)
                })

        else:

            failed_rows.append({
                "company_id": company,
                "metric_type": field,
                "original_text": value
            })

# ---------------------------------------
# Parsed CSV
# ---------------------------------------

parsed = pd.DataFrame(parsed_rows)

parsed.to_csv(
    "output/analysis_parsed.csv",
    index=False
)

# ---------------------------------------
# Failures CSV
# ---------------------------------------

failures = pd.DataFrame(failed_rows)

failures.to_csv(
    "output/parse_failures.csv",
    index=False
)

# ---------------------------------------
# Cross Validation
# ---------------------------------------

comparison = parsed.merge(
    ratios,
    on="company_id",
    how="left"
)

comparison["difference"] = None

for i, r in comparison.iterrows():

    if r["metric_type"] == "compounded_sales_growth":

        if pd.notna(r["revenue_cagr_5yr"]):

            comparison.loc[i, "difference"] = abs(
                r["value_pct"] - r["revenue_cagr_5yr"]
            )

    elif r["metric_type"] == "compounded_profit_growth":

        if pd.notna(r["pat_cagr_5yr"]):

            comparison.loc[i, "difference"] = abs(
                r["value_pct"] - r["pat_cagr_5yr"]
            )

comparison[
    comparison["difference"] > 5
].to_csv(
    "output/cagr_manual_review.csv",
    index=False
)

print("=" * 50)
print("NLP Parser Completed")
print("Parsed Records :", len(parsed))
print("Failed Records :", len(failures))
print(
    "Manual Review :",
    len(comparison[comparison["difference"] > 5])
)
print("=" * 50)