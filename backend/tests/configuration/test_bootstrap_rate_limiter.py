from backend.app.client.ratelimit.database_rate_limiter import DatabaseRateLimiter
from backend.app.client.ratelimit.in_memory_rate_limiter import InMemoryRateLimiter
from backend.app.configuration.admin.bootstrap_admin_settings import BootstrapAdminSettings
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.database.database_settings import DatabaseSettings
from backend.app.configuration.ratelimit.rate_limit_settings import RateLimitSettings
from backend.app.configuration.settings import Settings


def _settings(provider: str) -> Settings:
    return Settings(
        database=DatabaseSettings(url="sqlite://"),
        rate_limit=RateLimitSettings(provider=provider),
        bootstrap_admin=BootstrapAdminSettings(
            _env_file=None, email="", username="", full_name="", password=""
        ),
    )


def test_database_provider_selects_the_shared_limiter() -> None:
    assert isinstance(Bootstrap(_settings("database")).rate_limiter, DatabaseRateLimiter)


def test_the_default_provider_stays_in_memory() -> None:
    assert isinstance(Bootstrap(_settings("memory")).rate_limiter, InMemoryRateLimiter)
