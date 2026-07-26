import os
import sqlite3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore

# ============================================================
# STEP 1 - Load Data
# ============================================================

conn = sqlite3.connect("nifty100.db")

query = """
SELECT
    fr.company_id,
    fr.year,
    fr.return_on_equity_pct,
    fr.debt_to_equity,
    fr.revenue_cagr_5yr,
    fr.operating_profit_margin_pct,
    fr.free_cash_flow_cr,
    fr.net_profit_margin_pct,
    fr.asset_turnover,
    fr.interest_coverage,
    fr.earnings_per_share,
    fr.book_value_per_share,
    sc.broad_sector
FROM financial_ratios fr
LEFT JOIN sectors_clean sc
ON fr.company_id = sc.company_id
"""

df = pd.read_sql(query, conn)
conn.close()

print("=" * 60)
print("Rows loaded:", len(df))

# ============================================================
# STEP 2 - Latest Record Per Company
# ============================================================

df_latest = (
    df.sort_values("year")
      .groupby("company_id", as_index=False)
      .last()
)

print("Latest Companies:", len(df_latest))

# ============================================================
# STEP 3 - KPI Lists
# ============================================================

cluster_features = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "operating_profit_margin_pct",
    "free_cash_flow_cr"
]

heatmap_features = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "operating_profit_margin_pct",
    "free_cash_flow_cr",
    "net_profit_margin_pct",
    "asset_turnover",
    "interest_coverage",
    "earnings_per_share",
    "book_value_per_share"
]

# ============================================================
# STEP 4 - Load Cluster Labels
# ============================================================

cluster_labels = pd.read_csv("output/cluster_labels.csv")

df_latest = df_latest.merge(
    cluster_labels[["company_id", "cluster_id"]],
    on="company_id",
    how="left"
)

print("\nCluster Counts")
print(df_latest["cluster_id"].value_counts().sort_index())

# ============================================================
# STEP 5 - Cluster Profiling
# ============================================================

print("\n" + "=" * 60)
print("Cluster Mean")
print("=" * 60)

cluster_mean = (
    df_latest
    .groupby("cluster_id")[cluster_features]
    .mean()
)

print(cluster_mean)

print("\n" + "=" * 60)
print("Cluster Median")
print("=" * 60)

cluster_median = (
    df_latest
    .groupby("cluster_id")[cluster_features]
    .median()
)

print(cluster_median)

# ============================================================
# STEP 6 - Cluster Names
# ============================================================

cluster_names = {
    0: "High-Quality Compounders",
    1: "Emerging Growth",
    2: "Defensive Dividend Payers",
    3: "Value Cyclicals",
    4: "Distressed or Turnaround"
}

df_latest["cluster_name"] = (
    df_latest["cluster_id"]
    .map(cluster_names)
)

print("\nSample Cluster Assignments")

print(
    df_latest[
        [
            "company_id",
            "cluster_id",
            "cluster_name"
        ]
    ].head(10)
)
# ============================================================
# STEP 7 - Correlation Matrix Heatmap
# ============================================================

print("\n" + "=" * 60)
print("Generating Correlation Heatmap")
print("=" * 60)

corr = df_latest[heatmap_features].corr(method="pearson")

os.makedirs("reports", exist_ok=True)

plt.figure(figsize=(12, 8))

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

plt.title("Correlation Matrix (Latest Year)")

plt.tight_layout()

plt.savefig(
    "reports/correlation_heatmap.png",
    dpi=300
)

plt.close()

print("Saved: reports/correlation_heatmap.png")

# ============================================================
# STEP 8 - Sector-wise Outlier Detection (Z-score)
# ============================================================

print("\n" + "=" * 60)
print("Detecting Outliers")
print("=" * 60)

outlier_df = df_latest.copy()

for col in heatmap_features:

    outlier_df[col + "_z"] = (
        outlier_df
        .groupby("broad_sector")[col]
        .transform(
            lambda x: zscore(
                x,
                nan_policy="omit"
            )
        )
    )

z_columns = [
    c
    for c in outlier_df.columns
    if c.endswith("_z")
]

outlier_df["is_outlier"] = (
    outlier_df[z_columns]
    .abs()
    .gt(3)
    .any(axis=1)
)

outliers = outlier_df[
    outlier_df["is_outlier"]
]

os.makedirs("output", exist_ok=True)

outliers.to_csv(
    "output/outlier_report.csv",
    index=False
)

print("Total Outliers:", len(outliers))

print("Saved: output/outlier_report.csv")

if len(outliers) > 0:
    print("\nSample Outliers")

    print(
        outliers[
            [
                "company_id",
                "broad_sector"
            ]
        ].head()
    )
else:
    print("No outliers detected.")

# ============================================================
# STEP 9 - Portfolio Statistics
# ============================================================

print("\n" + "=" * 60)
print("Generating Portfolio Statistics")
print("=" * 60)

stats = []

for col in heatmap_features:

    stats.append({

        "KPI": col,

        "P10": df_latest[col].quantile(0.10),

        "P25": df_latest[col].quantile(0.25),

        "P50": df_latest[col].median(),

        "P75": df_latest[col].quantile(0.75),

        "P90": df_latest[col].quantile(0.90),

        "Mean": df_latest[col].mean(),

        "Std": df_latest[col].std()

    })

portfolio_stats = pd.DataFrame(stats)

os.makedirs("output", exist_ok=True)

portfolio_stats.to_csv(
    "output/portfolio_stats.csv",
    index=False
)

print("Saved: output/portfolio_stats.csv")

print("\nPortfolio Statistics Preview")

print(portfolio_stats)

# ============================================================
# STEP 10 - Save Cluster Profile Reports
# ============================================================

cluster_mean.to_csv(
    "output/cluster_profile_mean.csv"
)

cluster_median.to_csv(
    "output/cluster_profile_median.csv"
)

print("Saved: output/cluster_profile_mean.csv")
print("Saved: output/cluster_profile_median.csv")

# ============================================================
# STEP 11 - Summary
# ============================================================

print("\n" + "=" * 60)
print("DAY 37 COMPLETED SUCCESSFULLY")
print("=" * 60)

print(f"Companies Processed : {len(df_latest)}")
print(f"Clusters            : {df_latest['cluster_id'].nunique()}")
print(f"Outliers Detected   : {len(outliers)}")

print("\nGenerated Files")

print("reports/correlation_heatmap.png")
print("output/outlier_report.csv")
print("output/portfolio_stats.csv")
print("output/cluster_profile_mean.csv")
print("output/cluster_profile_median.csv")