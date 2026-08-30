from collections.abc import Callable
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, Request

from backend.app.client.ratelimit.provider import get_rate_limiter
from backend.app.client.ratelimit.rate_limiter import RateLimiter
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap


def _client_ip(request: Request) -> str:
    if request.client is None:
        return "unknown"
    return request.client.host


def rate_limited(bucket: str) -> Callable[..., None]:
    def dependency(
        request: Request,
        limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
        bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
    ) -> None:
        settings = bootstrap.settings.auth
        limiter.check(
            key=f"{bucket}:{_client_ip(request)}",
            limit=settings.rate_limit_max_attempts,
            window=timedelta(seconds=settings.rate_limit_window_seconds),
        )

    return dependency
