import os

def test_cashflow_module_exists():
    assert os.path.exists("src/analytics/cashflow_kpis.py")

def test_output_folder_exists():
    assert os.path.exists("output")