from abc import ABC, abstractmethod
from datetime import timedelta


class RateLimiter(ABC):
    @abstractmethod
    def check(self, key: str, limit: int, window: timedelta) -> None: ...
