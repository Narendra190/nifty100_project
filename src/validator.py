import pandas as pd
import os

processed_folder = "data/processed"

failures = []

for file in os.listdir(processed_folder):

    if file.endswith(".xlsx"):

        df = pd.read_excel(os.path.join(processed_folder, file))

        missing = df.isnull().sum().sum()

        duplicates = df.duplicated().sum()

        failures.append({
            "file": file,
            "missing_values": missing,
            "duplicate_rows": duplicates
        })

result = pd.DataFrame(failures)

result.to_excel(
    "output/validation_failures.xlsx",
    index=False,
    columns=["file", "missing_values", "duplicate_rows"]
)

print(result)
print("Validation completed!")