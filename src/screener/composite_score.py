import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

conn.close()

def normalize(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series([50] * len(series))

    return ((series - minimum) / (maximum - minimum)) * 100

df["roe_score"] = normalize(
    df["return_on_equity_pct"].fillna(0)
)

df["npm_score"] = normalize(
    df["net_profit_margin_pct"].fillna(0)
)

df["fcf_score"] = normalize(
    df["free_cash_flow_cr"].fillna(0)
)

df["revenue_score"] = normalize(
    df["revenue_cagr_5yr"].fillna(0)
)

df["pat_score"] = normalize(
    df["pat_cagr_5yr"].fillna(0)
)

df["de_score"] = 100 - normalize(
    df["debt_to_equity"].fillna(0)
)

df["icr_score"] = normalize(
    df["interest_coverage"].fillna(0)
)

df["composite_quality_score"] = (

    0.30 * df["roe_score"]

    + 0.15 * df["npm_score"]

    + 0.20 * df["fcf_score"]

    + 0.15 * df["revenue_score"]

    + 0.10 * df["pat_score"]

    + 0.05 * df["de_score"]

    + 0.05 * df["icr_score"]

)

print(df[[
    "company_id",
    "composite_quality_score"
]].head())

conn = sqlite3.connect("nifty100.db")

df.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("\nComposite Score Added Successfully")