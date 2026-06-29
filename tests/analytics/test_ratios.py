import pytest
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    check_opm_difference,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
)


# -------------------------------
# Net Profit Margin Tests
# -------------------------------

def test_net_profit_margin():
    assert net_profit_margin(100, 500) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


# -------------------------------
# Operating Profit Margin Tests
# -------------------------------

def test_operating_profit_margin():
    assert operating_profit_margin(150, 500) == 30.0


def test_opm_difference():
    assert check_opm_difference(25, 23) is True


def test_opm_no_difference():
    assert check_opm_difference(25, 24.5) is False


# -------------------------------
# ROE Tests
# -------------------------------

def test_roe():
    assert return_on_equity(100, 200, 300) == 20.0


def test_roe_negative_equity():
    assert return_on_equity(100, -200, 100) is None


# -------------------------------
# ROCE Tests
# -------------------------------

def test_roce():
    assert return_on_capital_employed(120, 300, 200, 100) == 20.0


# -------------------------------
# ROA Tests
# -------------------------------

def test_roa():
    assert return_on_assets(50, 500) == 10.0


def test_roa_zero_assets():
    assert return_on_assets(50, 0) is None