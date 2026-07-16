import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://test:test@127.0.0.1:1/test"
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client
