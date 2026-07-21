from pathlib import Path

import pandas as pd

from src.reports.tearsheet import _build_pdf_story


def test_build_pdf_story_uses_available_columns(tmp_path):
    companies = pd.DataFrame([
        {"company_id": "TEST", "company_name": "Test Company", "ticker": "TEST"}
    ])
    ratios = pd.DataFrame([
        {
            "company_id": "TEST",
            "year": "2024",
            "return_on_equity_pct": 12.0,
            "debt_to_equity": 0.5,
            "net_profit_margin_pct": 10.0,
            "earnings_per_share": 2.5,
        }
    ])
    cashflow = pd.DataFrame([
        {
            "company_id": "TEST",
            "year": "2024",
            "operating_activity": 100.0,
            "investing_activity": -20.0,
            "financing_activity": 5.0,
            "net_cash_flow": 85.0,
        }
    ])
    balance = pd.DataFrame([
        {
            "company_id": "TEST",
            "year": "2024",
            "equity_capital": 1000.0,
            "borrowings": 300.0,
            "other_liabilities": 50.0,
        }
    ])

    output_path = tmp_path / "test_tearsheet.pdf"

    _build_pdf_story("TEST", companies, ratios, cashflow, balance, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0
