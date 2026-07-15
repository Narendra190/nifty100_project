import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🏭 Sector Analysis")

conn = sqlite3.connect("nifty100.db")

sector = pd.read_sql(
    "SELECT * FROM sectors_clean",
    conn
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

market = pd.read_sql(
    "SELECT * FROM market_cap_clean",
    conn
)

conn.close()

sector_col = sector.columns[1]

selected = st.selectbox(
    "Sector",
    sorted(sector[sector_col].dropna().unique())
)

sector_df = sector[
    sector[sector_col] == selected
]

merged = sector_df.merge(
    market,
    on="company_id",
    how="left"
).merge(
    ratios,
    on="company_id",
    how="left"
)

fig = px.scatter(
    merged,
    x="market_cap_crore",
    y="return_on_equity_pct",
    size="market_cap_crore",
    hover_name="company_id"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

median = merged[
    [
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr"
    ]
].median()

st.bar_chart(median)