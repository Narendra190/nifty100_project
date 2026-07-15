import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💰 Capital Allocation")

df = pd.read_csv(
    "output/capital_allocation.csv"
)

fig = px.treemap(
    df,
    path=["pattern_label", "company_id"],
    values="year"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

pattern = st.selectbox(
    "Pattern",
    sorted(df["pattern_label"].unique())
)

st.dataframe(
    df[df.pattern_label == pattern]
)