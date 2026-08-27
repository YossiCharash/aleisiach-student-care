from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.utils.routes.security_headers_middleware import SecurityHeadersMiddleware


def _client(hsts_max_age_seconds: int | None) -> TestClient:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, hsts_max_age_seconds=hsts_max_age_seconds)

    @app.get("/ping")
    def ping() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


def test_static_security_headers_present() -> None:
    response = _client(None).get("/ping")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Content-Security-Policy"] == "frame-ancestors 'none'"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"


def test_hsts_omitted_when_not_configured() -> None:
    response = _client(None).get("/ping")

    assert "Strict-Transport-Security" not in response.headers


def test_hsts_present_when_configured() -> None:
    response = _client(31536000).get("/ping")

    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
