from fastapi import status
from fastapi.testclient import TestClient


def test_health_returns_expected_response(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "healthy": True,
        "status": "ok",
        "service": "SiteSignal",
        "version": "0.1.0",
    }
