import pandas as pd
import sqlite3
import os


def load_excel_to_table(file_path, table_name, conn):
    """
    Load one Excel file into a SQLite table.
    """
    df = pd.read_excel(file_path)

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    return len(df)


def load_all_files(folder="data/processed", db_name="nifty100.db"):
    """
    Load all Excel files from the processed folder.
    """
    conn = sqlite3.connect(db_name)

    for file in os.listdir(folder):

        if file.endswith(".xlsx"):

            table_name = file.replace(".xlsx", "")

            file_path = os.path.join(folder, file)

            rows = load_excel_to_table(file_path, table_name, conn)

            print(f"Loaded {table_name}: {rows} rows")

    conn.close()
    print("All files loaded successfully!")


if __name__ == "__main__":
    load_all_files()