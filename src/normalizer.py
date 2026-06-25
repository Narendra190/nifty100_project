import pandas as pd
import os


def normalize_columns(df):
    """
    Convert column names to lowercase and remove extra spaces.
    """

    # If the DataFrame has no columns, return it unchanged
    if len(df.columns) == 0:
        return df

    # Normalize column names
    df.columns = [str(col).strip().lower() for col in df.columns]

    return df


def remove_duplicates(df):
    """
    Remove duplicate rows.
    """
    return df.drop_duplicates()


def process_file(input_file, output_file):
    """
    Read, clean and save an Excel file.
    """
    df = pd.read_excel(input_file)

    df = normalize_columns(df)
    df = remove_duplicates(df)

    df.to_excel(output_file, index=False)


def process_all_files(raw_folder="data/raw",
                      processed_folder="data/processed"):

    os.makedirs(processed_folder, exist_ok=True)

    for file in os.listdir(raw_folder):

        if file.endswith(".xlsx"):

            input_path = os.path.join(raw_folder, file)

            output_path = os.path.join(
                processed_folder,
                file.replace(".xlsx", "_clean.xlsx")
            )

            process_file(input_path, output_path)

            print(f"Saved: {output_path}")


if __name__ == "__main__":
    process_all_files()