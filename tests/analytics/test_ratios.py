import os
import sys

sys.path.append(os.path.abspath("src"))

from analytics.ratios import *


def test_net_profit_margin():
    assert net_profit_margin(20, 100) == 20


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(20, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(30, 150) == 20


def test_operating_profit_margin_zero_sales():
    assert operating_profit_margin(30, 0) is None


def test_check_opm_difference_true():
    assert check_opm_difference(20, 18) is True


def test_check_opm_difference_false():
    assert check_opm_difference(20, 20.5) is False


def test_return_on_equity():
    assert return_on_equity(20, 50, 50) == 20


def test_return_on_equity_negative():
    assert return_on_equity(20, -100, 0) is None


def test_roce():
    assert return_on_capital_employed(30, 40, 40, 20) == 30


def test_roce_negative():
    assert return_on_capital_employed(30, -50, 0, 0) is None


def test_roa():
    assert return_on_assets(25, 100) == 25


def test_roa_zero_assets():
    assert return_on_assets(20, 0) is None


def test_debt_equity():
    assert debt_to_equity(50, 50, 50) == 0.5


def test_debt_equity_zero_borrowing():
    assert debt_to_equity(0, 50, 50) == 0


def test_debt_equity_negative_capital():
    assert debt_to_equity(20, -30, 0) is None


def test_high_leverage_true():
    assert high_leverage_flag(6, "Industrials") is True


def test_high_leverage_financials():
    assert high_leverage_flag(6, "Financials") is False


def test_interest_coverage():
    assert interest_coverage_ratio(100, 20, 10) == 12


def test_interest_zero():
    assert interest_coverage_ratio(100, 20, 0) is None


def test_icr_label():
    assert icr_label(None) == "Debt Free"


def test_icr_warning():
    assert icr_warning_flag(1.2) is True


def test_icr_warning_false():
    assert icr_warning_flag(3) is False


def test_net_debt():
    assert net_debt(100, 40) == 60


def test_asset_turnover():
    assert asset_turnover(200, 100) == 2


def test_asset_turnover_zero():
    assert asset_turnover(100, 0) is None