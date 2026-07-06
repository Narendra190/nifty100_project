import sqlite3
import pandas as pd
import yaml


def load_config(config_file="src/screener/screener_config.yaml"):
    with open(config_file, "r") as file:
        return yaml.safe_load(file)


def load_ratios(db="nifty100.db"):
    conn = sqlite3.connect(db)

    df = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    return df


def apply_filters(df, config):

    filters = config["filters"]

    if "return_on_equity_pct" in df.columns:
        df = df[
            df["return_on_equity_pct"] >=
            filters["roe_min"]
        ]

    if "debt_to_equity" in df.columns:
        df = df[
            df["debt_to_equity"] <=
            filters["debt_to_equity_max"]
        ]

    if "free_cash_flow_cr" in df.columns:
        df = df[
            df["free_cash_flow_cr"] >=
            filters["free_cash_flow_min"]
        ]

    if "revenue_cagr_5yr" in df.columns:
        df = df[
            df["revenue_cagr_5yr"] >=
            filters["revenue_cagr_5yr_min"]
        ]

    if "pat_cagr_5yr" in df.columns:
        df = df[
            df["pat_cagr_5yr"] >=
            filters["pat_cagr_5yr_min"]
        ]

    if "operating_profit_margin_pct" in df.columns:
        df = df[
            df["operating_profit_margin_pct"] >=
            filters["operating_profit_margin_min"]
        ]

    if "interest_coverage" in df.columns:
        df = df[
            (
                df["interest_coverage"] >=
                filters["interest_coverage_min"]
            )
            |
            (
                df["interest_coverage"].isna()
            )
        ]

    if "asset_turnover" in df.columns:
        df = df[
            df["asset_turnover"] >=
            filters["asset_turnover_min"]
        ]

    if "composite_quality_score" not in df.columns:
        df["composite_quality_score"] = 0

    df = df.sort_values(
        by="return_on_equity_pct",
        ascending=False
    )

    return df


if __name__ == "__main__":

    config = load_config()

    ratios = load_ratios()

    screened = apply_filters(
        ratios,
        config
    )

    print(screened.head())

    print()

    print("Companies Passed:", len(screened))