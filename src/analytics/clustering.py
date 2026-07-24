import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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
    sc.broad_sector
FROM financial_ratios fr
LEFT JOIN sectors_clean sc
ON fr.company_id = sc.company_id
"""

df = pd.read_sql(query, conn)
conn.close()

print("=" * 60)
print("Raw Dataset")
print("=" * 60)
print(df.head())

print("\nColumns:")
print(df.columns.tolist())

print("\nShape:")
print(df.shape)

# ============================================================
# STEP 2 - Latest Record Per Company
# ============================================================

df_latest = (
    df.sort_values("year")
      .groupby("company_id", as_index=False)
      .last()
)

print("\n" + "=" * 60)
print("Latest Company Records")
print("=" * 60)
print(df_latest.head())

print("\nLatest Dataset Shape:")
print(df_latest.shape)

print("\nNumber of Unique Companies:")
print(df_latest["company_id"].nunique())

print("\nMissing Values:")
print(df_latest.isnull().sum())

# ============================================================
# STEP 3 - Select Features
# ============================================================

features = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "operating_profit_margin_pct",
    "free_cash_flow_cr"
]

print("\nSelected Features:")
print(df_latest[features].head())

# ============================================================
# STEP 4 - Handle Missing Values
# ============================================================

print("\n" + "=" * 60)
print("Handling Missing Values")
print("=" * 60)

df_latest["broad_sector"] = df_latest["broad_sector"].fillna("Unknown")

for col in features:
    df_latest[col] = (
        df_latest.groupby("broad_sector")[col]
        .transform(lambda x: x.fillna(x.median()))
    )

for col in features:
    df_latest[col] = df_latest[col].fillna(df_latest[col].median())

print("\nMissing values after imputation:")
print(df_latest[features + ["broad_sector"]].isnull().sum())

# ============================================================
# STEP 5 - Handle Extreme Outliers
# ============================================================

print("\n" + "=" * 60)
print("Handling Extreme ROE Values")
print("=" * 60)

df_latest["return_on_equity_pct"] = (
    df_latest["return_on_equity_pct"].clip(-100, 100)
)

print("Maximum ROE after clipping:",
      df_latest["return_on_equity_pct"].max())

# ============================================================
# STEP 6 - Feature Scaling
# ============================================================

print("\n" + "=" * 60)
print("Scaling Features")
print("=" * 60)

scaler = StandardScaler()

X_scaled = scaler.fit_transform(df_latest[features])

scaled_df = pd.DataFrame(
    X_scaled,
    columns=features
)

print("Scaled Dataset Shape:", X_scaled.shape)

print("\nScaled Feature Means:")
print(scaled_df.mean())

print("\nScaled Feature Standard Deviations:")
print(scaled_df.std())

# ============================================================
# STEP 7 - KMeans Clustering
# ============================================================

print("\n" + "=" * 60)
print("Running KMeans")
print("=" * 60)

kmeans = KMeans(
    n_clusters=5,
    random_state=42,
    n_init=10
)

df_latest["cluster_id"] = kmeans.fit_predict(X_scaled)

print(df_latest[["company_id", "cluster_id"]].head())

print("\nCluster Counts:")
print(df_latest["cluster_id"].value_counts().sort_index())

# ============================================================
# STEP 8 - Elbow Plot
# ============================================================

print("\n" + "=" * 60)
print("Generating Elbow Plot")
print("=" * 60)

inertia = []

for k in range(2, 11):
    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )
    model.fit(X_scaled)
    inertia.append(model.inertia_)

os.makedirs("reports", exist_ok=True)

plt.figure(figsize=(8, 5))
plt.plot(range(2, 11), inertia, marker="o")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.title("Elbow Method")
plt.grid(True)

plt.savefig("reports/elbow_plot.png", dpi=300)
plt.close()

print("Saved: reports/elbow_plot.png")

# ============================================================
# STEP 9 - Distance from Centroid
# ============================================================

print("\n" + "=" * 60)
print("Calculating Distances")
print("=" * 60)

distances = kmeans.transform(X_scaled)

df_latest["distance_from_centroid"] = [
    distances[i][cluster]
    for i, cluster in enumerate(df_latest["cluster_id"])
]

print(
    df_latest[
        ["company_id", "cluster_id", "distance_from_centroid"]
    ].head()
)

# ============================================================
# STEP 10 - Cluster Names
# ============================================================

cluster_names = {
    0: "Stable Performers",
    1: "Highly Leveraged Growth",
    2: "Exceptional ROE",
    3: "High Margin Leaders",
    4: "Cash Burners"
}

df_latest["cluster_name"] = (
    df_latest["cluster_id"].map(cluster_names)
)

# ============================================================
# STEP 11 - Cluster Centroids
# ============================================================

centroids = pd.DataFrame(
    scaler.inverse_transform(kmeans.cluster_centers_),
    columns=features
)

print("\nCluster Centroids:")
print(centroids)

# ============================================================
# STEP 12 - Export Results
# ============================================================

os.makedirs("output", exist_ok=True)

output = df_latest[
    [
        "company_id",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid"
    ]
]

output.to_csv(
    "output/cluster_labels.csv",
    index=False
)

print("\nSaved: output/cluster_labels.csv")

print("\nTop 10 ROE Values After Clipping:")
print(
    df_latest.nlargest(10, "return_on_equity_pct")[
        ["company_id", "return_on_equity_pct"]
    ]
)