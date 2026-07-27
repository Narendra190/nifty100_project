import os
import sys
import pandas as pd

sys.path.append(os.path.abspath("src"))

from validator import validate_dataframe


def test_missing_values():

    df = pd.DataFrame({
        "A":[1,None],
        "B":[2,3]
    })

    result = validate_dataframe(df)

    assert result["missing_values"] == 1


def test_duplicate_rows():

    df = pd.DataFrame({
        "A":[1,1],
        "B":[2,2]
    })

    result = validate_dataframe(df)

    assert result["duplicate_rows"] == 1


def test_clean_dataframe():

    df = pd.DataFrame({
        "A":[1,2],
        "B":[3,4]
    })

    result = validate_dataframe(df)

    assert result["missing_values"] == 0
    assert result["duplicate_rows"] == 0


def test_only_missing():

    df = pd.DataFrame({
        "A":[None,None]
    })

    result = validate_dataframe(df)

    assert result["missing_values"] == 2


def test_only_duplicates():

    df = pd.DataFrame({
        "A":[1,1,1]
    })

    result = validate_dataframe(df)

    assert result["duplicate_rows"] == 2


def test_empty_dataframe():

    df = pd.DataFrame()

    result = validate_dataframe(df)

    assert result["missing_values"] == 0
    assert result["duplicate_rows"] == 0