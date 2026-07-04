import sqlite3
import pandas as pd
import os

os.makedirs("output", exist_ok=True)

conn = sqlite3.connect("nifty100.db")

companies = pd.read_sql("SELECT * FROM companies_clean", conn)
ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)

log = []

for _, row in companies.iterrows():

    company = row["company_id"]

    r = ratios[ratios["company_id"] == company]

    if r.empty:
        continue

    r = r.iloc[0]

    if "roce_percentage" in row.index:

        if pd.notna(r["return_on_equity_pct"]):

            diff = abs(
                row["roce_percentage"] -
                r["return_on_equity_pct"]
            )

            if diff > 5:

                log.append({
                    "company": company,
                    "metric": "ROCE",
                    "difference": round(diff, 2),
                    "category": "Version Difference"
                })
    if "roe_percentage" in row.index:

        if pd.notna(r["return_on_equity_pct"]):

            diff = abs(
                row["roe_percentage"] -
                r["return_on_equity_pct"]
            )

            if diff > 5:

                log.append({
                    "company": company,
                    "metric": "ROE",
                    "difference": round(diff, 2),
                    "category": "Data Source Issue"
                })

log_df = pd.DataFrame(log)

log_df.to_csv(
    "output/ratio_edge_cases.csv",
    index=False
)

print(log_df.head())

print("\nEdge case report generated.")