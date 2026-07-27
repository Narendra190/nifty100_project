import os
import sys
import tempfile
import pandas as pd

sys.path.append(os.path.abspath("src"))

from normalizer import (
    normalize_columns,
    remove_duplicates,
    process_file,
    process_all_files,
)


def test_normalize_columns_lowercase():
    df = pd.DataFrame(columns=["Name", "AGE"])
    result = normalize_columns(df)
    assert list(result.columns) == ["name", "age"]


def test_normalize_columns_strip_spaces():
    df = pd.DataFrame(columns=[" Name ", " Age "])
    result = normalize_columns(df)
    assert list(result.columns) == ["name", "age"]


def test_normalize_columns_numbers():
    df = pd.DataFrame(columns=[1, 2])
    result = normalize_columns(df)
    assert list(result.columns) == ["1", "2"]


def test_normalize_columns_empty():
    df = pd.DataFrame()
    result = normalize_columns(df)
    assert result.empty


def test_remove_duplicates():
    df = pd.DataFrame({"A": [1, 1, 2]})
    result = remove_duplicates(df)
    assert len(result) == 2


def test_remove_duplicates_no_duplicates():
    df = pd.DataFrame({"A": [1, 2, 3]})
    result = remove_duplicates(df)
    assert len(result) == 3


def test_process_file(tmp_path):
    input_file = tmp_path / "sample.xlsx"
    output_file = tmp_path / "sample_clean.xlsx"

    df = pd.DataFrame({
        " Name ": ["A", "A", "B"],
        " Age ": [20, 20, 25]
    })

    df.to_excel(input_file, index=False)

    process_file(input_file, output_file)

    assert output_file.exists()

    cleaned = pd.read_excel(output_file)

    assert list(cleaned.columns) == ["name", "age"]
    assert len(cleaned) == 2


def test_process_all_files(tmp_path):
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"

    raw.mkdir()

    df = pd.DataFrame({" Name ": [1, 1, 2]})

    df.to_excel(raw / "test.xlsx", index=False)

    process_all_files(raw, processed)

    assert (processed / "test_clean.xlsx").exists()


def test_process_all_files_multiple():
    with tempfile.TemporaryDirectory() as raw:
        with tempfile.TemporaryDirectory() as processed:

            pd.DataFrame({"A":[1]}).to_excel(
                os.path.join(raw,"a.xlsx"),
                index=False
            )

            pd.DataFrame({"B":[2]}).to_excel(
                os.path.join(raw,"b.xlsx"),
                index=False
            )

            process_all_files(raw, processed)

            assert len(os.listdir(processed)) == 2


def test_normalize_columns_special_chars():
    df = pd.DataFrame(columns=[" Company Name ", "Market Cap"])
    result = normalize_columns(df)
    assert list(result.columns) == ["company name", "market cap"]