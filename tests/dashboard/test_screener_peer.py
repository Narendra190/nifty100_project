import os

def test_screener_exists():
    assert os.path.exists(
        "src/dashboard/pages/03_screener.py"
    )

def test_peer_exists():
    assert os.path.exists(
        "src/dashboard/pages/04_peers.py"
    )