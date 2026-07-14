import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🏠 Nifty 100 Analytics Dashboard")
conn = sqlite3.connect("nifty100.db")
ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
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
years = sorted(ratios["year"].dropna().unique())
selected_year = st.sidebar.selectbox(
    "Select Year",
    years
)

filtered = ratios[
    ratios["year"] == selected_year
]

c1, c2, c3 = st.columns(3)

c4, c5, c6 = st.columns(3)

c1.metric(
    "Average ROE",
    round(filtered["return_on_equity_pct"].mean(), 2)
)

c2.metric(
    "Median D/E",
    round(filtered["debt_to_equity"].median(), 2)
)

c3.metric(
    "Companies",
    filtered["company_id"].nunique()
)

c4.metric(
    "Revenue CAGR",
    round(filtered["revenue_cagr_5yr"].median(), 2)
)

c5.metric(
    "Debt Free",
    len(filtered[
        filtered["debt_to_equity"] == 0
    ])
)

c6.metric(
    "Composite Score",
    round(filtered["composite_quality_score"].mean(), 2)
)

sector_counts = sectors.iloc[:, 1].value_counts()
fig = px.pie(
    names=sector_counts.index,
    values=sector_counts.values,
    hole=0.5,
    title="Sector Distribution"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Top Companies")
top = filtered.sort_values(
    "composite_quality_score",
    ascending=False
).head(5)
st.dataframe(top)