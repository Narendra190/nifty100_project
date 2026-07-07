import sqlite3
import pandas as pd

def load_data():
    conn = sqlite3.connect("nifty100.db")
    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )
    conn.close()
    return df

def quality_compounder(df):
    return df[
        (df["return_on_equity_pct"] > 15) &
        (df["debt_to_equity"] < 1) &
        (df["free_cash_flow_cr"] > 0) &
        (df["revenue_cagr_5yr"] > 10)
    ]

def value_pick(df):
    result = df.copy()

    if "book_value_per_share" in result.columns:
        result = result[result["book_value_per_share"] < 3]

    result = result[
        result["debt_to_equity"] < 2
    ]

    return result

def growth_accelerator(df):
    return df[
        (df["pat_cagr_5yr"] > 20) &
        (df["revenue_cagr_5yr"] > 15) &
        (df["debt_to_equity"] < 2)
    ]

def dividend_champion(df):
    return df[
        (df["dividend_payout_ratio_pct"] < 80) &
        (df["free_cash_flow_cr"] > 0)
    ]

def debt_free_bluechip(df):
    return df[
        (df["debt_to_equity"] == 0) &
        (df["return_on_equity_pct"] > 12)
    ]

def turnaround_watch(df):
    result = df.copy()

    if "free_cash_flow_cr" in result.columns:

        result = result[
            result["free_cash_flow_cr"] > 0
        ]
    return result

if __name__ == "__main__":
    ratios = load_data()

    presets = {
        "Quality Compounder": quality_compounder(ratios),
        "Value Pick": value_pick(ratios),
        "Growth Accelerator": growth_accelerator(ratios),
        "Dividend Champion": dividend_champion(ratios),
        "Debt-Free Blue Chip": debt_free_bluechip(ratios),
        "Turnaround Watch": turnaround_watch(ratios)
    }

    for name, result in presets.items():
        print("=" * 60)
        print(name)
        print("Companies:", len(result))
        print(result.head())