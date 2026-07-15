import streamlit as st
import sqlite3
import pandas as pd

st.title("📊 Financial Screener")

conn = sqlite3.connect("nifty100.db")

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

companies = pd.read_sql(
    "SELECT company_id FROM companies_clean",
    conn
)

conn.close()

# Sidebar Filters
st.sidebar.header("Filters")

roe = st.sidebar.slider(
    "Minimum ROE",
    -100.0,
    300.0,
    15.0
)

de = st.sidebar.slider(
    "Maximum D/E",
    0.0,
    10.0,
    1.0
)

fcf = st.sidebar.slider(
    "Minimum Free Cash Flow",
    -10000.0,
    100000.0,
    0.0
)

revenue = st.sidebar.slider(
    "Revenue CAGR",
    -100.0,
    100.0,
    0.0
)

pat = st.sidebar.slider(
    "PAT CAGR",
    -100.0,
    100.0,
    0.0
)

opm = st.sidebar.slider(
    "Operating Profit Margin",
    -50.0,
    100.0,
    0.0
)

icr = st.sidebar.slider(
    "Interest Coverage",
    0.0,
    100.0,
    1.0
)

# Presets
st.subheader("Quick Presets")

c1, c2, c3 = st.columns(3)

if c1.button("Quality"):
    roe = 15
    de = 1

if c2.button("Growth"):
    revenue = 15
    pat = 20

if c3.button("Debt-Free"):
    de = 0

filtered = ratios[
    (ratios["return_on_equity_pct"] >= roe) &
    (ratios["debt_to_equity"] <= de) &
    (ratios["free_cash_flow_cr"] >= fcf) &
    (ratios["revenue_cagr_5yr"] >= revenue) &
    (ratios["pat_cagr_5yr"] >= pat) &
    (ratios["operating_profit_margin_pct"] >= opm) &
    (ratios["interest_coverage"] >= icr)
]

st.success(f"{len(filtered)} companies match your filters")

st.dataframe(filtered)

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV",
    csv,
    "screener_output.csv",
    "text/csv"
)