from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.client.database.provider import get_session
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.main import create_app


@pytest.fixture
def limited_api(db_session: Session) -> Iterator[TestClient]:
    app = create_app()

    def override_session() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_login_blocks_after_rate_limit(limited_api: TestClient) -> None:
    limit = AuthSettings().rate_limit_max_attempts
    payload = {"username": "ghost", "password": "password123"}

    for _ in range(limit):
        assert limited_api.post("/auth/login", json=payload).status_code == 401

    blocked = limited_api.post("/auth/login", json=payload)
    assert blocked.status_code == 429
    assert blocked.json()["code"] == "rate_limited"


def test_rate_limit_buckets_are_per_endpoint(limited_api: TestClient) -> None:
    limit = AuthSettings().rate_limit_max_attempts
    payload = {"username": "ghost", "password": "password123"}
    for _ in range(limit):
        assert limited_api.post("/auth/login", json=payload).status_code == 401

    reset = limited_api.post("/auth/password-reset/request", json={"email": "nobody@example.com"})
    assert reset.status_code == 202
