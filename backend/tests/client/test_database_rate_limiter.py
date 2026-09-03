from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select

from backend.app.client.database.database import Database
from backend.app.client.ratelimit.database_rate_limiter import DatabaseRateLimiter
from backend.app.configuration.database.database_settings import DatabaseSettings
from backend.app.errors.service.rate_limit_exceeded_error import RateLimitExceededError
from backend.app.models.base import Base
from backend.app.models.client.rate_limit_hit import RateLimitHit
from backend.tests.support.fake_clock import FakeClock

WINDOW = timedelta(seconds=60)
KEY = "login:1.2.3.4"


@pytest.fixture
def database(tmp_path: Path) -> Iterator[Database]:
    url = f"sqlite:///{tmp_path / 'ratelimit.db'}"
    schema_engine = create_engine(url, future=True)
    Base.metadata.create_all(schema_engine)
    schema_engine.dispose()

    yield Database(DatabaseSettings(url=url))


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 9, 3, 10, 0, tzinfo=UTC))


def _stored_hits(database: Database) -> list[RateLimitHit]:
    generator = database.session()
    session = next(generator)
    try:
        return list(session.scalars(select(RateLimitHit)))
    finally:
        next(generator, None)


def test_allows_attempts_up_to_the_limit(database: Database, clock: FakeClock) -> None:
    limiter = DatabaseRateLimiter(database, clock)

    for _ in range(3):
        limiter.check(KEY, 3, WINDOW)


def test_rejects_the_attempt_past_the_limit(database: Database, clock: FakeClock) -> None:
    limiter = DatabaseRateLimiter(database, clock)
    for _ in range(3):
        limiter.check(KEY, 3, WINDOW)

    with pytest.raises(RateLimitExceededError):
        limiter.check(KEY, 3, WINDOW)


def test_a_rejected_attempt_is_not_recorded(database: Database, clock: FakeClock) -> None:
    limiter = DatabaseRateLimiter(database, clock)
    for _ in range(3):
        limiter.check(KEY, 3, WINDOW)
    with pytest.raises(RateLimitExceededError):
        limiter.check(KEY, 3, WINDOW)

    assert len(_stored_hits(database)) == 3


def test_each_key_gets_its_own_quota(database: Database, clock: FakeClock) -> None:
    limiter = DatabaseRateLimiter(database, clock)
    for _ in range(3):
        limiter.check(KEY, 3, WINDOW)

    limiter.check("login:5.6.7.8", 3, WINDOW)


def test_the_window_slides(database: Database, clock: FakeClock) -> None:
    limiter = DatabaseRateLimiter(database, clock)
    for _ in range(3):
        limiter.check(KEY, 3, WINDOW)
    clock.moment += WINDOW + timedelta(seconds=1)

    limiter.check(KEY, 3, WINDOW)


def test_two_limiters_on_one_database_share_a_single_quota(
    database: Database, clock: FakeClock
) -> None:
    first = DatabaseRateLimiter(database, clock)
    second = DatabaseRateLimiter(database, clock)
    first.check(KEY, 3, WINDOW)
    first.check(KEY, 3, WINDOW)
    second.check(KEY, 3, WINDOW)

    with pytest.raises(RateLimitExceededError):
        second.check(KEY, 3, WINDOW)


def test_the_hit_is_committed_by_the_limiter_itself(database: Database, clock: FakeClock) -> None:
    DatabaseRateLimiter(database, clock).check(KEY, 3, WINDOW)

    stored = _stored_hits(database)

    assert len(stored) == 1
    assert stored[0].bucket_key == KEY
