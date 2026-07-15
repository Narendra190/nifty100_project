import os

def test_trends():
    assert os.path.exists(
        "src/dashboard/pages/05_trends.py"
    )

def test_sector():
    assert os.path.exists(
        "src/dashboard/pages/06_sectors.py"
    )

def test_capital():
    assert os.path.exists(
        "src/dashboard/pages/07_capital.py"
    )

def test_reports():
    assert os.path.exists(
        "src/dashboard/pages/08_reports.py"
    )