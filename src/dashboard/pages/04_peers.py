import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

st.title("👥 Peer Comparison")

conn = sqlite3.connect("nifty100.db")

peer = pd.read_sql(
    "SELECT * FROM peer_percentiles",
    conn
)

conn.close()

groups = sorted(
    peer["peer_group_name"].dropna().unique()
)

group = st.selectbox(
    "Peer Group",
    groups
)

df = peer[
    peer["peer_group_name"] == group
]

companies = sorted(
    df["company_id"].unique()
)

company = st.selectbox(
    "Company",
    companies
)

metrics = df[
    df["company_id"] == company
]

peer_avg = (
    df.groupby("metric")["value"]
      .mean()
      .reset_index()
)

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=metrics["value"],
        theta=metrics["metric"],
        fill="toself",
        name=company
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=peer_avg["value"],
        theta=peer_avg["metric"],
        name="Peer Average"
    )
)

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    showlegend=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader("Peer Ranking")

pivot = (
    df.pivot_table(
        index="company_id",
        columns="metric",
        values="value"
    )
)

st.dataframe(pivot)