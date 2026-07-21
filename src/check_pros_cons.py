import pandas as pd

df = pd.read_csv("output/pros_cons_generated.csv")

print("Columns:")
print(df.columns.tolist())

print("\nFirst 10 Rows:")
print(df.head(10))