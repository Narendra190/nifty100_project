import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("reports/radar_charts", exist_ok=True)

conn = sqlite3.connect("nifty100.db")

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

peer = pd.read_sql(
    "SELECT * FROM peer_groups_clean",
    conn
)

conn.close()

company_col = None
peer_col = None

for col in peer.columns:

    name = col.lower()

    if company_col is None and ("company" in name or "ticker" in name):
        company_col = col

    if peer_col is None and ("peer" in name or "group" in name):
        peer_col = col

peer = peer[[company_col, peer_col]]

df = ratios.merge(
    peer,
    left_on="company_id",
    right_on=company_col,
    how="left"
)

metrics = [

    "return_on_equity_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "asset_turnover",
    "composite_quality_score"
]

labels = [
    "ROE",
    "NPM",
    "D/E",
    "FCF",
    "PAT CAGR",
    "Revenue CAGR",
    "Asset Turnover",
    "Composite"
]

angles = np.linspace(
    0,
    2 * np.pi,
    len(labels),
    endpoint=False
).tolist()
angles += angles[:1]

for company in df["company_id"].unique():
    company_df = df[df["company_id"] == company]
    row = company_df.iloc[0]
    values = []
    for metric in metrics:
        value = row.get(metric, 0)
        if pd.isna(value):
            value = 0
        values.append(float(value))
    values += values[:1]
    peer_name = row[peer_col]

    if pd.isna(peer_name):
        peer_values = [0] * len(metrics)
    else:
        peer_df = df[df[peer_col] == peer_name]
        peer_values = []

        for metric in metrics:
            peer_values.append(
                peer_df[metric].fillna(0).mean()
            )

    peer_values += peer_values[:1]
    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(
        111,
        polar=True
    )

    ax.plot(
        angles,
        values,
        linewidth=2,
        label=company
    )

    ax.fill(
        angles,
        values,
        alpha=0.25
    )

    ax.plot(
        angles,
        peer_values,
        linestyle="dashed",
        linewidth=2,
        label="Peer Avg"
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=9
    )

    plt.title(company)
    plt.legend(
        loc="upper right"
    )

    plt.savefig(
        f"reports/radar_charts/{company}_radar.png",
        dpi=150
    )

    plt.close()
print("Radar Charts Generated Successfully!")