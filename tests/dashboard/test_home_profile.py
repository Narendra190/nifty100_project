import os

def test_home_exists():
    assert os.path.exists("src/dashboard/pages/01_home.py")

def test_profile_exists():
    assert os.path.exists("src/dashboard/pages/02_profile.py")