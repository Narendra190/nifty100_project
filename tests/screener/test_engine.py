import pandas as pd

from src.screener.engine import apply_filters


def test_roe_filter():

    df = pd.DataFrame({

        "return_on_equity_pct": [10, 20],

        "debt_to_equity": [0.5, 0.5],

        "free_cash_flow_cr": [10, 10],

        "revenue_cagr_5yr": [10, 10],

        "pat_cagr_5yr": [10, 10],

        "operating_profit_margin_pct": [20, 20],

        "interest_coverage": [5, 5],

        "asset_turnover": [1, 1]

    })

    config = {
        "filters": {
            "roe_min": 15,
            "debt_to_equity_max": 1,
            "free_cash_flow_min": 0,
            "revenue_cagr_5yr_min": 5,
            "pat_cagr_5yr_min": 5,
            "operating_profit_margin_min": 10,
            "interest_coverage_min": 2,
            "asset_turnover_min": 0.5
        }
    }

    result = apply_filters(df, config)

    assert len(result) == 1