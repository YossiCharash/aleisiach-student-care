import pytest

from backend.app.configuration.app.app_settings import AppSettings


def test_single_origin_from_env_is_not_json_decoded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_CORS_ORIGINS", "http://localhost:8080")

    settings = AppSettings()

    assert settings.cors_origins == ["http://localhost:8080"]


def test_comma_separated_origins_from_env_are_split(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_CORS_ORIGINS", "http://localhost:8080, https://app.aleisiach.org")

    settings = AppSettings()

    assert settings.cors_origins == [
        "http://localhost:8080",
        "https://app.aleisiach.org",
    ]
