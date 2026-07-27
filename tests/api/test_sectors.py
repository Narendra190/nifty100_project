from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_all_sectors():

    response = client.get("/api/v1/sectors/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 10


def test_sector_companies():

    response = client.get(
        "/api/v1/sectors/Information%20Technology/companies"
    )

    assert response.status_code == 200

    assert len(response.json()) > 0


def test_invalid_sector():

    response = client.get(
        "/api/v1/sectors/Test/companies"
    )

    assert response.status_code == 404