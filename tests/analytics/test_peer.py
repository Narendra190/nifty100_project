import pandas as pd


def test_peer_dataframe():

    df = pd.DataFrame({

        "company_id": ["A", "B"],

        "peer_group_name": ["IT", "IT"],

        "return_on_equity_pct": [20, 30]

    })

    assert len(df) == 2