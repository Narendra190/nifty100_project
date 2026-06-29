def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin = Net Profit / Sales × 100
    """
    if sales == 0:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin = Operating Profit / Sales × 100
    """
    if sales == 0:
        return None
    return (operating_profit / sales) * 100


def check_opm_difference(calculated_opm, existing_opm):
    """
    Return True if difference is greater than 1%
    """
    if calculated_opm is None or existing_opm is None:
        return False

    return abs(calculated_opm - existing_opm) > 1


def return_on_equity(net_profit, equity, reserves):
    """
    ROE = Net Profit / (Equity + Reserves) × 100
    """
    capital = equity + reserves

    if capital <= 0:
        return None

    return (net_profit / capital) * 100


def return_on_capital_employed(ebit, equity, reserves, borrowings):
    """
    ROCE = EBIT / (Equity + Reserves + Borrowings) × 100
    """
    capital = equity + reserves + borrowings

    if capital <= 0:
        return None

    return (ebit / capital) * 100


def return_on_assets(net_profit, total_assets):
    """
    ROA = Net Profit / Total Assets × 100
    """
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100