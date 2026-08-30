from datetime import UTC, datetime, timedelta

import pytest

from backend.app.client.ratelimit.in_memory_rate_limiter import InMemoryRateLimiter
from backend.app.errors.service.rate_limit_exceeded_error import RateLimitExceededError
from backend.tests.support.fake_clock import FakeClock

_BASE = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
_WINDOW = timedelta(seconds=60)


def test_allows_up_to_the_limit() -> None:
    limiter = InMemoryRateLimiter(FakeClock(_BASE))

    for _ in range(3):
        limiter.check("key", limit=3, window=_WINDOW)


def test_blocks_beyond_the_limit() -> None:
    limiter = InMemoryRateLimiter(FakeClock(_BASE))
    for _ in range(3):
        limiter.check("key", limit=3, window=_WINDOW)

    with pytest.raises(RateLimitExceededError):
        limiter.check("key", limit=3, window=_WINDOW)


def test_separate_keys_have_independent_counters() -> None:
    limiter = InMemoryRateLimiter(FakeClock(_BASE))
    for _ in range(3):
        limiter.check("a", limit=3, window=_WINDOW)

    limiter.check("b", limit=3, window=_WINDOW)


def test_window_expiry_frees_capacity() -> None:
    clock = FakeClock(_BASE)
    limiter = InMemoryRateLimiter(clock)
    for _ in range(3):
        limiter.check("key", limit=3, window=_WINDOW)

    clock.moment = _BASE + timedelta(seconds=61)
    limiter.check("key", limit=3, window=_WINDOW)


def test_idle_keys_are_evicted_to_bound_memory() -> None:
    clock = FakeClock(_BASE)
    limiter = InMemoryRateLimiter(clock)
    for index in range(5):
        limiter.check(f"key-{index}", limit=3, window=_WINDOW)

    clock.moment = _BASE + timedelta(seconds=61)
    limiter.check("fresh", limit=3, window=_WINDOW)

    assert list(limiter._hits.keys()) == ["fresh"]
