from pathlib import Path

import pandas as pd
from PyPDF2 import PdfReader

from src.reports.tearsheet import _build_pdf_story, generate_portfolio_summary_pdf


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


def test_generate_portfolio_summary_pdf_creates_multiple_pages(tmp_path):
    companies = pd.DataFrame([
        {"company_id": "TEST1", "company_name": "Alpha Corp", "ticker": "ALPHA", "sector": "Energy"},
        {"company_id": "TEST2", "company_name": "Beta Ltd", "ticker": "BETA", "sector": "Materials"},
    ])
    ratios = pd.DataFrame([
        {
            "company_id": "TEST1",
            "year": "2024",
            "sales": 100.0,
            "net_profit": 20.0,
            "return_on_equity_pct": 15.0,
            "debt_to_equity": 0.4,
            "operating_profit_margin_pct": 18.0,
        },
        {
            "company_id": "TEST2",
            "year": "2024",
            "sales": 90.0,
            "net_profit": 12.0,
            "return_on_equity_pct": 10.0,
            "debt_to_equity": 0.8,
            "operating_profit_margin_pct": 16.0,
        },
    ])
    cashflow = pd.DataFrame([
        {
            "company_id": "TEST1",
            "year": "2024",
            "operating_activity": 50.0,
            "investing_activity": -10.0,
            "financing_activity": 5.0,
            "net_cash_flow": 45.0,
        },
        {
            "company_id": "TEST2",
            "year": "2024",
            "operating_activity": 40.0,
            "investing_activity": -8.0,
            "financing_activity": 4.0,
            "net_cash_flow": 36.0,
        },
    ])
    balance = pd.DataFrame([
        {
            "company_id": "TEST1",
            "year": "2024",
            "equity_capital": 1000.0,
            "borrowings": 300.0,
            "other_liabilities": 50.0,
        },
        {
            "company_id": "TEST2",
            "year": "2024",
            "equity_capital": 900.0,
            "borrowings": 250.0,
            "other_liabilities": 60.0,
        },
    ])

    output_path = tmp_path / "portfolio_summary.pdf"

    result = generate_portfolio_summary_pdf(
        companies=companies,
        ratios=ratios,
        cashflow=cashflow,
        balance=balance,
        output_path=str(output_path),
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert result == output_path

    reader = PdfReader(str(output_path))
    assert len(reader.pages) == 2
