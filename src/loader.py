import pandas as pd
import os

folder = "data/raw"

for file in os.listdir(folder):
    if file.endswith(".xlsx"):
        df = pd.read_excel(os.path.join(folder, file))
        print(f"{file}: {df.shape}")