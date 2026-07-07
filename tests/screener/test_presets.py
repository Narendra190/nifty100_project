import pandas as pd
from src.screener.presets import quality_compounder

def test_quality_compounder():
    df = pd.DataFrame({
        "return_on_equity_pct": [20, 10],
        "debt_to_equity": [0.5, 2],
        "free_cash_flow_cr": [100, -10],
        "revenue_cagr_5yr": [15, 5]
    })

    result = quality_compounder(df)
    assert len(result) == 1