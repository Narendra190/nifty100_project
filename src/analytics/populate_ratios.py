import sys
import os
import sqlite3
import pandas as pd

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
)

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
)

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)

# -----------------------------------
# Connect Database
# -----------------------------------

conn = sqlite3.connect("nifty100.db")

# -----------------------------------
# Read Tables
# -----------------------------------

profit = pd.read_sql(
    "SELECT * FROM profitandloss_clean",
    conn
)

balance = pd.read_sql(
    "SELECT * FROM balancesheet_clean",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow_clean",
    conn
)

rows = []

# -----------------------------------
# Build Financial Ratios
# -----------------------------------

for _, p in profit.iterrows():

    company_id = p["company_id"]
    year = p["year"]

    b = balance[
        (balance["company_id"] == company_id) &
        (balance["year"] == year)
    ]

    c = cashflow[
        (cashflow["company_id"] == company_id) &
        (cashflow["year"] == year)
    ]

    if b.empty or c.empty:
        continue

    b = b.iloc[0]
    c = c.iloc[0]

    fcf = free_cash_flow(
        c["operating_activity"],
        c["investing_activity"]
    )

    revenue5, _ = revenue_cagr(
        p["sales"],
        p["sales"],
        5
    )

    pat5, _ = pat_cagr(
        p["net_profit"],
        p["net_profit"],
        5
    )

    eps5, _ = eps_cagr(
        p["eps"],
        p["eps"],
        5
    )

    if b["equity_capital"] != 0:
        book_value = (
            b["equity_capital"] +
            b["reserves"]
        ) / b["equity_capital"]
    else:
        book_value = None

    rows.append({

        "company_id": company_id,

        "year": year,

        "net_profit_margin_pct":
            net_profit_margin(
                p["net_profit"],
                p["sales"]
            ),

        "operating_profit_margin_pct":
            operating_profit_margin(
                p["operating_profit"],
                p["sales"]
            ),

        "return_on_equity_pct":
            return_on_equity(
                p["net_profit"],
                b["equity_capital"],
                b["reserves"]
            ),

        "debt_to_equity":
            debt_to_equity(
                b["borrowings"],
                b["equity_capital"],
                b["reserves"]
            ),

        "interest_coverage":
            interest_coverage_ratio(
                p["operating_profit"],
                p["other_income"],
                p["interest"]
            ),

        "asset_turnover":
            asset_turnover(
                p["sales"],
                b["total_assets"]
            ),

        "free_cash_flow_cr":
            fcf,

        "capex_cr":
            abs(c["investing_activity"]),

        "earnings_per_share":
            p["eps"],

        "book_value_per_share":
            book_value,

        "dividend_payout_ratio_pct":
            p["dividend_payout"],

        "total_debt_cr":
            b["borrowings"],

        "cash_from_operations_cr":
            c["operating_activity"],

        "revenue_cagr_5yr":
            revenue5,

        "pat_cagr_5yr":
            pat5,

        "eps_cagr_5yr":
            eps5,

        "composite_quality_score":
            None

    })

# -----------------------------------
# Save to SQLite
# -----------------------------------

ratio_df = pd.DataFrame(rows)

ratio_df.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

print("=" * 50)
print("Financial Ratio Engine Completed")
print("Rows Loaded:", len(ratio_df))
print("=" * 50)

conn.close()