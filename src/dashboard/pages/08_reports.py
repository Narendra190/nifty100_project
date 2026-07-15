import streamlit as st
import sqlite3
import pandas as pd

st.title("📑 Annual Reports")

conn = sqlite3.connect("nifty100.db")

docs = pd.read_sql(
    "SELECT * FROM documents_clean",
    conn
)

conn.close()

company = st.selectbox(
    "Company",
    sorted(docs["company_id"].unique())
)

data = docs[
    docs["company_id"] == company
]

if data.empty:

    st.error("🔴 Report unavailable")

else:

    st.subheader("Available Annual Reports")

    for _, row in data.iterrows():

        st.markdown(
            f"[📄 {row['Year']} Annual Report]({row['Annual_Report']})"
        )