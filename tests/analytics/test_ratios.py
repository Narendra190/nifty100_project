import pytest
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    check_opm_difference,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)


def test_net_profit_margin():
    assert net_profit_margin(100, 500) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(150, 500) == 30.0


def test_opm_difference():
    assert check_opm_difference(25, 23) is True


def test_opm_no_difference():
    assert check_opm_difference(25, 24.5) is False


def test_roe():
    assert return_on_equity(100, 200, 300) == 20.0


def test_roe_negative_equity():
    assert return_on_equity(100, -200, 100) is None


def test_roce():
    assert return_on_capital_employed(120, 300, 200, 100) == 20.0


def test_roa():
    assert return_on_assets(50, 500) == 10.0


def test_roa_zero_assets():
    assert return_on_assets(50, 0) is None


def test_debt_to_equity():
    assert debt_to_equity(200, 100, 100) == 1


def test_debt_free_returns_zero():
    assert debt_to_equity(0, 100, 100) == 0


def test_high_leverage_flag():
    assert high_leverage_flag(6, "Technology") is True


def test_high_leverage_financials():
    assert high_leverage_flag(6, "Financials") is False


def test_interest_coverage():
    assert interest_coverage_ratio(100, 20, 10) == 12


def test_interest_zero():
    assert interest_coverage_ratio(100, 20, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2