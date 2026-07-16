import os

def test_valuation_script_exists():

    assert os.path.exists(
        "src/analytics/valuation.py"
    )

def test_output_folder_exists():

    assert os.path.exists(
        "output"
    )