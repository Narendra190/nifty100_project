import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.title("🏢 Company Profile")
conn = sqlite3.connect("nifty100.db")
companies = pd.read_sql(
    "SELECT * FROM companies_clean",
    conn
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

profit = pd.read_sql(
    "SELECT * FROM profitandloss_clean",
    conn
)

conn.close()
ticker = st.selectbox(
    "Select Company",
    sorted(companies["company_id"].unique())

)

company = companies[
    companies["company_id"] == ticker
]

if company.empty:
    st.error(
        "Ticker not found — please try another."
    )

    st.stop()
company = company.iloc[0]
st.header(company["company_id"])
cols = st.columns(3)
latest = ratios[
    ratios["company_id"] == ticker
].sort_values(
    "year"
)

latest = latest.iloc[-1]

cols[0].metric(
    "ROE",
    round(
        latest["return_on_equity_pct"],
        2
    )
)

cols[1].metric(
    "D/E",
    round(
        latest["debt_to_equity"],
        2
    )
)

cols[2].metric(
    "Revenue CAGR",
    round(
        latest["revenue_cagr_5yr"],
        2
    )
)

history = profit[
    profit["company_id"] == ticker
]

if not history.empty:
    fig = px.bar(
        history,
        x="year",
        y=["sales", "net_profit"],
        barmode="group",
        title="Revenue vs Net Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

roe = ratios[
    ratios["company_id"] == ticker
]

if not roe.empty:
    fig = px.line(
        roe,
        x="year",
        y="return_on_equity_pct",
        title="ROE Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.success("✔ Pros and Cons module will be added in Sprint 4.")