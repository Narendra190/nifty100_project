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