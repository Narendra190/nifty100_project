import pandas as pd
import os

raw_folder = "data/raw"
processed_folder = "data/processed"

for file in os.listdir(raw_folder):
    if file.endswith(".xlsx"):

        df = pd.read_excel(os.path.join(raw_folder, file))

        df.columns = df.columns.str.strip().str.lower()

        df = df.drop_duplicates()

        output_file = file.replace(".xlsx", "_clean.xlsx")

        df.to_excel(
            os.path.join(processed_folder, output_file),
            index=False
        )

        print(f"Saved: {output_file}")