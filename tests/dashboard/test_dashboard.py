import os

def test_dashboard_exists():
    assert os.path.exists(
        "src/dashboard/app.py"
    )

def test_db_exists():
    assert os.path.exists(
        "src/dashboard/utils/db.py"
    )