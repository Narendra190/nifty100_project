import os

def test_qa_exists():
    assert os.path.exists(
        "src/dashboard/qa_test.py"
    )