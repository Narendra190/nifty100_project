import pandas as pd
from analytics.cashflow_kpis import export_capital_allocation
data = pd.DataFrame({"company_id": ["TCS"],
    "year": [2024],
    "cfo_sign": ["+"],
    "cfi_sign": ["-"],
    "cff_sign": ["-"],
    "pattern_label": ["Reinvestor"]})
export_capital_allocation(data)
print("capital_allocation.csv generated successfully")