import threading
from collections import deque
from datetime import datetime, timedelta

from backend.app.client.ratelimit.rate_limiter import RateLimiter
from backend.app.errors.service.rate_limit_exceeded_error import RateLimitExceededError
from backend.app.utils.service.clock import Clock


class InMemoryRateLimiter(RateLimiter):
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._hits: dict[str, deque[datetime]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window: timedelta) -> None:
        now = self._clock.now()
        threshold = now - window
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= threshold:
                hits.popleft()
            if len(hits) >= limit:
                raise RateLimitExceededError
            hits.append(now)
