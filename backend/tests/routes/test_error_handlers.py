import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from backend.app.client.whatsapp.whatsapp_notifier import WhatsAppNotifier
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.settings import Settings
from backend.app.errors.routes.error_handlers import register_error_handlers
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.schema.service.error_alert import ErrorAlert
from backend.app.service.alerts.error_alert_service import ErrorAlertService
from backend.app.utils.service.clock import Clock


class _CapturingNotifier(WhatsAppNotifier):
    def __init__(self) -> None:
        self.alerts: list[ErrorAlert] = []

    def notify(self, alert: ErrorAlert) -> None:
        self.alerts.append(alert)


class _Body(BaseModel):
    name: str


@pytest.fixture
def notifier() -> _CapturingNotifier:
    return _CapturingNotifier()


@pytest.fixture
def client(notifier: _CapturingNotifier) -> TestClient:
    app = FastAPI()
    bootstrap = Bootstrap(Settings())
    bootstrap.error_alert_service = ErrorAlertService(
        notifier=notifier,
        clock=Clock(),
        environment="test",
        enabled=True,
    )
    app.state.bootstrap = bootstrap
    register_error_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("kaboom")

    @app.get("/missing")
    def missing() -> None:
        raise NotFoundError("Student")

    @app.post("/echo")
    def echo(body: _Body) -> dict[str, str]:
        return {"name": body.name}

    return TestClient(app, raise_server_exceptions=False)


def test_unexpected_error_returns_safe_500_and_dispatches_alert(
    client: TestClient, notifier: _CapturingNotifier
) -> None:
    response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body["code"] == "internal_error"
    assert body["reference"]
    assert "kaboom" not in body["message"]
    assert len(notifier.alerts) == 1
    assert notifier.alerts[0].reference == body["reference"]
    assert notifier.alerts[0].path == "/boom"


def test_app_error_passes_through_without_alert(
    client: TestClient, notifier: _CapturingNotifier
) -> None:
    response = client.get("/missing")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
    assert notifier.alerts == []


def test_validation_error_returns_field_envelope(
    client: TestClient, notifier: _CapturingNotifier
) -> None:
    response = client.post("/echo", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    assert body["fields"]
    assert notifier.alerts == []


def test_unknown_route_returns_hebrew_not_found_message(
    client: TestClient, notifier: _CapturingNotifier
) -> None:
    response = client.get("/no-such-route")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "http_error"
    assert body["message"] == "המשאב המבוקש לא נמצא."
    assert notifier.alerts == []
