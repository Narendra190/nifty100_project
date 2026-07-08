import pandas as pd


def test_score_exists():

    df = pd.DataFrame({

        "return_on_equity_pct": [20],

        "net_profit_margin_pct": [15],

        "free_cash_flow_cr": [100],

        "revenue_cagr_5yr": [10],

        "pat_cagr_5yr": [10],

        "debt_to_equity": [0.5],

        "interest_coverage": [5]

    })

    assert "return_on_equity_pct" in df.columns