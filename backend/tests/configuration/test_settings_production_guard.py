import pytest
from pydantic import ValidationError

from backend.app.configuration.admin.bootstrap_admin_settings import BootstrapAdminSettings
from backend.app.configuration.app.app_settings import AppSettings
from backend.app.configuration.database.database_settings import DatabaseSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.configuration.settings import Settings

_SAFE_DB_URL = "postgresql+psycopg://app:strong-secret@db.internal:5432/aleisiach"


def _production_app() -> AppSettings:
    return AppSettings(
        environment="production",
        trusted_proxy_count=1,
        cors_origins=["https://app.aleisiach.org"],
    )


def test_local_environment_allows_development_defaults() -> None:
    Settings(app=AppSettings(environment="local"))


def test_production_rejects_console_email_and_default_database() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app=AppSettings(environment="production", trusted_proxy_count=1),
            email=EmailSettings(provider="console"),
        )


def test_production_rejects_zero_trusted_proxies() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app=AppSettings(
                environment="production",
                trusted_proxy_count=0,
                cors_origins=["https://app.aleisiach.org"],
            ),
            database=DatabaseSettings(url=_SAFE_DB_URL),
            email=EmailSettings(provider="smtp"),
        )


def test_production_accepts_hardened_configuration() -> None:
    Settings(
        app=_production_app(),
        database=DatabaseSettings(url=_SAFE_DB_URL),
        email=EmailSettings(provider="smtp"),
    )


def _shipped_admin() -> BootstrapAdminSettings:
    return BootstrapAdminSettings(
        _env_file=None,
        email="admin@example.org",
        username="admin",
        full_name="System Administrator",
        password="change-me-123",
    )


def test_production_rejects_the_env_example_admin_password() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app=_production_app(),
            database=DatabaseSettings(url=_SAFE_DB_URL),
            email=EmailSettings(provider="smtp"),
            bootstrap_admin=_shipped_admin(),
        )


def test_production_accepts_a_bootstrap_admin_with_its_own_password() -> None:
    admin = _shipped_admin()
    admin.password = "a-real-secret-2026"

    Settings(
        app=_production_app(),
        database=DatabaseSettings(url=_SAFE_DB_URL),
        email=EmailSettings(provider="smtp"),
        bootstrap_admin=admin,
    )
