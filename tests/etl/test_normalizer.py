import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath("src"))

from normalizer import normalize_columns, remove_duplicates


# -------------------------------
# normalize_columns() Tests
# -------------------------------

def test_columns_lowercase():
    df = pd.DataFrame(columns=["Name", "AGE"])
    df = normalize_columns(df)
    assert list(df.columns) == ["name", "age"]


def test_columns_strip_spaces():
    df = pd.DataFrame(columns=[" Name ", " Age "])
    df = normalize_columns(df)
    assert list(df.columns) == ["name", "age"]


def test_single_column():
    df = pd.DataFrame(columns=[" Company "])
    df = normalize_columns(df)
    assert list(df.columns) == ["company"]


def test_empty_dataframe():
    df = pd.DataFrame()
    df = normalize_columns(df)
    assert list(df.columns) == []


def test_multiple_columns():
    df = pd.DataFrame(columns=["Ticker", "Close Price", "Volume"])
    df = normalize_columns(df)
    assert list(df.columns) == ["ticker", "close price", "volume"]


# -------------------------------
# remove_duplicates() Tests
# -------------------------------

def test_remove_duplicate_rows():
    df = pd.DataFrame({"A": [1, 1, 2]})
    df = remove_duplicates(df)
    assert len(df) == 2


def test_no_duplicates():
    df = pd.DataFrame({"A": [1, 2, 3]})
    df = remove_duplicates(df)
    assert len(df) == 3


def test_duplicate_strings():
    df = pd.DataFrame({"Name": ["A", "A", "B"]})
    df = remove_duplicates(df)
    assert len(df) == 2


def test_duplicate_multiple_columns():
    df = pd.DataFrame({
        "A": [1, 1],
        "B": [2, 2]
    })
    df = remove_duplicates(df)
    assert len(df) == 1


def test_empty_duplicate():
    df = pd.DataFrame()
    df = remove_duplicates(df)
    assert df.empty