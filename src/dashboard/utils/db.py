import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "nifty100.db"


@st.cache_data(ttl=600)
def run_query(query, params=None):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        query,
        conn,
        params=params
    )

    conn.close()

    return df


@st.cache_data(ttl=600)
def get_companies():

    return run_query("""
    SELECT *
    FROM companies
    """)


@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    if year:

        return run_query("""
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        AND year=?
        """, (ticker, year))

    return run_query("""
    SELECT *
    FROM financial_ratios
    WHERE company_id=?
    """, (ticker,))


@st.cache_data(ttl=600)
def get_pl(ticker):

    return run_query("""
    SELECT *
    FROM profitandloss_clean
    WHERE company_id=?
    """, (ticker,))


@st.cache_data(ttl=600)
def get_bs(ticker):

    return run_query("""
    SELECT *
    FROM balancesheet_clean
    WHERE company_id=?
    """, (ticker,))


@st.cache_data(ttl=600)
def get_cf(ticker):

    return run_query("""
    SELECT *
    FROM cashflow_clean
    WHERE company_id=?
    """, (ticker,))


@st.cache_data(ttl=600)
def get_sectors():

    return run_query("""
    SELECT *
    FROM sectors_clean
    """)


@st.cache_data(ttl=600)
def get_peers(group_name):

    return run_query("""
    SELECT *
    FROM peer_groups_clean
    WHERE peer_group_name=?
    """, (group_name,))


@st.cache_data(ttl=600)
def get_valuation(ticker):

    return run_query("""
    SELECT *
    FROM financial_ratios
    WHERE company_id=?
    """, (ticker,))