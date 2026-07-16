from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

import app.main as app_main


def successful_database_check() -> None:
    pass


def failed_database_check() -> None:
    raise SQLAlchemyError("simulated database outage")


def test_readiness_returns_200(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        app_main,
        "check_database_connection",
        successful_database_check,
    )

    response = client.get("/ready")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "ready": True,
        "status": "ok",
        "service": "SiteSignal",
    }


def test_readiness_returns_503_when_database_is_unavailable(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        app_main,
        "check_database_connection",
        failed_database_check,
    )

    response = client.get("/ready")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {
        "detail": "Database is unavailable.",
    }
