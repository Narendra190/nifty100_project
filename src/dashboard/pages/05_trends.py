import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("📈 Trend Analysis")

conn = sqlite3.connect("nifty100.db")

profit = pd.read_sql(
    "SELECT * FROM profitandloss_clean",
    conn
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

conn.close()

company = st.selectbox(
    "Company",
    sorted(profit["company_id"].unique())
)

metrics = st.multiselect(
    "Select up to 3 Metrics",
    [
        "sales",
        "net_profit",
        "return_on_equity_pct",
        "operating_profit_margin_pct"
    ],
    default=["sales"]
)

if len(metrics) > 3:
    st.warning("Select a maximum of 3 metrics.")
    st.stop()

pl = profit[profit.company_id == company].copy()
rt = ratios[ratios.company_id == company].copy()

merged = pd.merge(
    pl,
    rt,
    on=["company_id", "year"],
    how="left"
)

fig = px.line(
    merged,
    x="year",
    y=metrics,
    markers=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)