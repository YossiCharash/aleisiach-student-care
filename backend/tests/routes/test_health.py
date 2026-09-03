from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_disclose_the_environment(client: TestClient) -> None:
    response = client.get("/health")

    assert "environment" not in response.json()
