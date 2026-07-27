from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health():

    response = client.get("/api/v1/health/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    tables = data["db_row_counts"]

    assert len(tables) == 10

    expected = [
        "companies_clean",
        "balancesheet_clean",
        "cashflow_clean",
        "profitandloss_clean",
        "stock_prices",
        "financial_ratios",
        "sectors_clean",
        "peer_groups_clean",
        "documents_clean",
        "analysis_clean",
    ]

    for table in expected:
        assert table in tables