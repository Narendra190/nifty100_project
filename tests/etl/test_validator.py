import pandas as pd

from src.validator import validate_dataframe


def test_no_missing_values():
    df = pd.DataFrame({
        "A": [1, 2],
        "B": [3, 4]
    })

    result = validate_dataframe(df)

    assert result["missing_values"] == 0


def test_missing_values():
    df = pd.DataFrame({
        "A": [1, None],
        "B": [3, None]
    })

    result = validate_dataframe(df)

    assert result["missing_values"] == 2


def test_no_duplicates():
    df = pd.DataFrame({
        "A": [1, 2, 3]
    })

    result = validate_dataframe(df)

    assert result["duplicate_rows"] == 0


def test_duplicate_rows():
    df = pd.DataFrame({
        "A": [1, 1, 2]
    })

    result = validate_dataframe(df)

    assert result["duplicate_rows"] == 1


def test_missing_and_duplicates():
    df = pd.DataFrame({
        "A": [1, 1, None]
    })

    result = validate_dataframe(df)

    assert result["missing_values"] == 1
    assert result["duplicate_rows"] == 1


def test_empty_dataframe():
    df = pd.DataFrame()

    result = validate_dataframe(df)

    assert result["missing_values"] == 0
    assert result["duplicate_rows"] == 0