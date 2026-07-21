import pandas as pd

from src.analytics.cashflow_kpis import *


def test_free_cash_flow():
    assert free_cash_flow(100, -30) == 70


def test_negative_fcf():
    assert free_cash_flow(50, -100) == -50


def test_cfo_quality_high():
    assert cfo_quality_score([100, 120], [80, 100]) == "High Quality"


def test_cfo_quality_none():
    assert cfo_quality_score([100], [0]) is None


def test_capex_asset_light():
    value, label = capex_intensity(-20, 1000)
    assert label == "Asset Light"


def test_fcf_conversion():
    assert fcf_conversion_rate(80, 100) == 80


def test_fcf_conversion_zero():
    assert fcf_conversion_rate(80, 0) is None


def test_reinvestor():
    _, _, _, label = capital_allocation_pattern(100, -50, -30, 0.8)
    assert label == "Reinvestor"


def test_shareholder_returns():
    _, _, _, label = capital_allocation_pattern(100, -50, -30, 1.2)
    assert label == "Shareholder Returns"


def test_growth_funded_by_debt():
    _, _, _, label = capital_allocation_pattern(-100, -50, 80)
    assert label == "Growth Funded by Debt"


def test_summarize_pattern_distribution_counts_latest_year():
    report = pd.DataFrame([
        {"company_id": "A", "year": "2022", "pattern_label": "Reinvestor"},
        {"company_id": "B", "year": "2022", "pattern_label": "Reinvestor"},
        {"company_id": "C", "year": "2022", "pattern_label": "Growth Funded by Debt"},
        {"company_id": "A", "year": "2023", "pattern_label": "Distress Signal"},
        {"company_id": "B", "year": "2023", "pattern_label": "Reinvestor"},
    ])

    summary = summarize_pattern_distribution(report, latest_year="2023")

    assert summary["Reinvestor"] == 1
    assert summary["Distress Signal"] == 1
    assert summary["Growth Funded by Debt"] == 0


def test_build_pattern_change_report_detects_transitions():
    report = pd.DataFrame([
        {"company_id": "A", "year": "2022", "pattern_label": "Reinvestor"},
        {"company_id": "A", "year": "2023", "pattern_label": "Distress Signal"},
        {"company_id": "B", "year": "2022", "pattern_label": "Cash Accumulator"},
        {"company_id": "B", "year": "2023", "pattern_label": "Cash Accumulator"},
    ])

    changes = build_pattern_change_report(report)

    assert len(changes) == 1
    assert changes.iloc[0]["company_id"] == "A"
    assert changes.iloc[0]["pattern_from"] == "Reinvestor"
    assert changes.iloc[0]["pattern_to"] == "Distress Signal"


def test_build_capital_allocation_report_completes_company_year_matrix():
    cashflow = pd.DataFrame([
        {"company_id": "A", "year": "2022", "operating_activity": 100, "investing_activity": -50, "financing_activity": -30},
        {"company_id": "A", "year": "2023", "operating_activity": -100, "investing_activity": 50, "financing_activity": 80},
        {"company_id": "B", "year": "2022", "operating_activity": 100, "investing_activity": -50, "financing_activity": -30},
    ])

    report = build_capital_allocation_report(
        cashflow_df=cashflow,
        company_ids=["A", "B"],
        years=["2022", "2023"],
        profit_df=pd.DataFrame([
            {"company_id": "A", "year": "2022", "net_profit": 50},
            {"company_id": "A", "year": "2023", "net_profit": 10},
            {"company_id": "B", "year": "2022", "net_profit": 100},
        ]),
    )

    assert report.shape[0] == 4
    assert set(report["company_id"]) == {"A", "B"}
    assert set(report["year"]) == {"2022", "2023"}
    assert report.loc[(report["company_id"] == "A") & (report["year"] == "2023"), "pattern_label"].iloc[0] == "Distress Signal"