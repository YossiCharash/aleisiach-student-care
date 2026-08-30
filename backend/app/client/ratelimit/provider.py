from typing import Annotated

from fastapi import Depends

from backend.app.client.ratelimit.rate_limiter import RateLimiter
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap


def get_rate_limiter(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> RateLimiter:
    return bootstrap.rate_limiter
