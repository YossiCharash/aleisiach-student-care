from typing import Annotated

from fastapi import Depends, Request

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.utils.routes.rate_limit import client_ip

_MAX_IP_LENGTH = 45
_MAX_USER_AGENT_LENGTH = 400


def _clipped(value: str | None, limit: int) -> str | None:
    return value[:limit] if value else None


def get_auth_event_context(
    request: Request,
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> AuthEventContext:
    return AuthEventContext(
        ip=_clipped(client_ip(request, bootstrap.settings.app.trusted_proxy_count), _MAX_IP_LENGTH),
        user_agent=_clipped(request.headers.get("user-agent"), _MAX_USER_AGENT_LENGTH),
    )
