from datetime import datetime, timedelta

from backend.app.client.database.database import Database
from backend.app.client.ratelimit.rate_limit_repository import RateLimitRepository
from backend.app.client.ratelimit.rate_limiter import RateLimiter
from backend.app.errors.service.rate_limit_exceeded_error import RateLimitExceededError
from backend.app.utils.service.clock import Clock


class DatabaseRateLimiter(RateLimiter):
    def __init__(self, database: Database, clock: Clock) -> None:
        self._database = database
        self._clock = clock

    def check(self, key: str, limit: int, window: timedelta) -> None:
        now = self._clock.now()
        if self._record_unless_exhausted(key, limit, now - window, now):
            return
        raise RateLimitExceededError

    def _record_unless_exhausted(
        self, key: str, limit: int, threshold: datetime, now: datetime
    ) -> bool:
        generator = self._database.session()
        session = next(generator)
        try:
            repository = RateLimitRepository(session)
            if repository.count_since(key, threshold) >= limit:
                return False
            repository.add(key, now)
            return True
        except BaseException:
            session.rollback()
            raise
        finally:
            next(generator, None)
