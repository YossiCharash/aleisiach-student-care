from starlette.datastructures import Headers

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.settings import Settings
from backend.app.models.client.audit_log import AuditLog
from backend.app.utils.routes.request_context import get_auth_event_context


class _StubClient:
    host = "10.0.0.7"


class _StubRequest:
    def __init__(self, headers: dict[str, str]) -> None:
        self.headers = Headers(headers)
        self.client = _StubClient()


def _bootstrap(trusted_proxy_count: int) -> Bootstrap:
    settings = Settings()
    settings.app.trusted_proxy_count = trusted_proxy_count
    return Bootstrap(settings)


def _column_length(name: str) -> int:
    return int(AuditLog.__table__.columns[name].type.length)


def test_peer_address_is_used_without_trusted_proxies() -> None:
    context = get_auth_event_context(_StubRequest({}), _bootstrap(0))

    assert context.ip == "10.0.0.7"


def test_oversized_forwarded_for_is_clipped_to_the_column() -> None:
    request = _StubRequest({"x-forwarded-for": "A" * 300})

    context = get_auth_event_context(request, _bootstrap(1))

    assert context.ip is not None
    assert len(context.ip) == _column_length("ip")


def test_oversized_user_agent_is_clipped_to_the_column() -> None:
    request = _StubRequest({"user-agent": "B" * 900})

    context = get_auth_event_context(request, _bootstrap(0))

    assert context.user_agent is not None
    assert len(context.user_agent) == _column_length("user_agent")


def test_absent_headers_stay_none() -> None:
    context = get_auth_event_context(_StubRequest({}), _bootstrap(0))

    assert context.user_agent is None
