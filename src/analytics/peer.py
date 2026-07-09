import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

# Load tables
ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

peer_groups = pd.read_sql(
    "SELECT * FROM peer_groups_clean",
    conn
)

company_col = None
peer_col = None

for col in peer_groups.columns:
    name = col.lower()

    if company_col is None and ("company" in name or "ticker" in name):
        company_col = col

    if peer_col is None and ("peer" in name or "group" in name):
        peer_col = col

if company_col is None or peer_col is None:
    print("No peer group assigned")
    conn.close()
    exit()

df = ratios.merge(
    peer_groups[[company_col, peer_col]],
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
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover"
]

rows = []

for group in df[peer_col].dropna().unique():

    group_df = df[df[peer_col] == group]

    for metric in metrics:

        if metric not in group_df.columns:
            continue

        ranks = group_df[metric].rank(
            pct=True,
            ascending=True
        )

        if metric == "debt_to_equity":
            ranks = 1 - ranks

        for idx, value in group_df.iterrows():

            rows.append({

                "company_id":
                    value["company_id"],

                "peer_group_name":
                    group,

                "metric":
                    metric,

                "value":
                    value[metric],

                "percentile_rank":
                    ranks.loc[idx],

                "year":
                    value["year"]

            })

peer_df = pd.DataFrame(rows)

peer_df.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False
)

print("=" * 50)
print("Peer Percentiles Generated")
print("Rows:", len(peer_df))
print("=" * 50)

conn.close()