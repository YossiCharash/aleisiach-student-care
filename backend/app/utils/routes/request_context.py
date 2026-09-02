from typing import Annotated

from fastapi import Depends, Request

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.provider import get_bootstrap
from backend.app.schema.service.auth_event_context import AuthEventContext
from backend.app.utils.routes.rate_limit import client_ip

_MAX_USER_AGENT_LENGTH = 400


def get_auth_event_context(
    request: Request,
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> AuthEventContext:
    user_agent = request.headers.get("user-agent")
    return AuthEventContext(
        ip=client_ip(request, bootstrap.settings.app.trusted_proxy_count),
        user_agent=user_agent[:_MAX_USER_AGENT_LENGTH] if user_agent else None,
    )
