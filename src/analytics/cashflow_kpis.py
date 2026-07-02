import pandas as pd


def free_cash_flow(operating_activity, investing_activity):
    return operating_activity + investing_activity

def cfo_quality_score(cfo_list, pat_list):
    ratios = []

    for cfo, pat in zip(cfo_list, pat_list):
        if pat == 0:
            continue
        ratios.append(cfo / pat)

    if len(ratios) == 0:
        return None

    avg_ratio = sum(ratios) / len(ratios)

    if avg_ratio > 1:
        return "High Quality"

    elif avg_ratio >= 0.5:
        return "Moderate"

    else:
        return "Accrual Risk"


def capex_intensity(investing_activity, sales):
    if sales == 0:
        return None

    intensity = abs(investing_activity) / sales * 100

    if intensity < 3:
        label = "Asset Light"

    elif intensity <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


def fcf_conversion_rate(fcf, operating_profit):
    if operating_profit == 0:
        return None

    return (fcf / operating_profit) * 100


def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=1):

    cfo_sign = "+" if cfo >= 0 else "-"
    cfi_sign = "+" if cfi >= 0 else "-"
    cff_sign = "+" if cff >= 0 else "-"

    signs = (cfo_sign, cfi_sign, cff_sign)

    mapping = {
        ("+", "-", "-"): "Shareholder Returns" if cfo_pat_ratio > 1 else "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    return (
        cfo_sign,
        cfi_sign,
        cff_sign,
        mapping.get(signs, "Unknown")
    )


def export_capital_allocation(df, output_file="output/capital_allocation.csv"):
    df.to_csv(output_file, index=False)