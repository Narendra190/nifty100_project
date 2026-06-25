import pandas as pd
import os


def validate_dataframe(df):
    """
    Validate a dataframe and return missing values and duplicate rows.
    """
    missing = df.isnull().sum().sum()
    duplicates = df.duplicated().sum()

    return {
        "missing_values": missing,
        "duplicate_rows": duplicates
    }


def validate_file(file_path):
    """
    Validate a single Excel file.
    """
    df = pd.read_excel(file_path)
    return validate_dataframe(df)


def validate_all(processed_folder="data/processed",
                 output_file="output/validation_failures.xlsx"):

    failures = []

    for file in os.listdir(processed_folder):

        if file.endswith(".xlsx"):

            result = validate_file(
                os.path.join(processed_folder, file)
            )

            result["file"] = file

            failures.append(result)

    result_df = pd.DataFrame(failures)

    result_df.to_excel(output_file, index=False)

    print(result_df)

    print("Validation completed!")


if __name__ == "__main__":
    validate_all()