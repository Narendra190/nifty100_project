import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Nifty 100 Analytics Dashboard")
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Screen",
    [
        "Home",
        "Company Profile",
        "Screener",
        "Peers",
        "Trends",
        "Sectors",
        "Capital",
        "Reports"
    ]
)
st.header(page)
st.write(
    "This page will be implemented during Sprint 4."
)