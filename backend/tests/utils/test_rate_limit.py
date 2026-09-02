from starlette.requests import Request

from backend.app.utils.routes.rate_limit import client_ip


def _request(headers: dict[str, str], client: tuple[str, int] | None) -> Request:
    raw_headers = [(key.lower().encode(), value.encode()) for key, value in headers.items()]
    return Request({"type": "http", "headers": raw_headers, "client": client})


def test_uses_peer_address_when_no_proxy_is_trusted() -> None:
    request = _request({"x-forwarded-for": "9.9.9.9"}, ("10.0.0.1", 1234))

    assert client_ip(request, trusted_proxy_count=0) == "10.0.0.1"


def test_takesclient_ip_from_forwarded_header_behind_one_proxy() -> None:
    request = _request({"x-forwarded-for": "203.0.113.7"}, ("10.0.0.1", 1234))

    assert client_ip(request, trusted_proxy_count=1) == "203.0.113.7"


def test_ignores_spoofed_leftmost_forwarded_entries() -> None:
    request = _request({"x-forwarded-for": "1.1.1.1, 203.0.113.7"}, ("10.0.0.1", 1234))

    assert client_ip(request, trusted_proxy_count=1) == "203.0.113.7"


def test_falls_back_to_unknown_when_client_missing() -> None:
    request = _request({}, None)

    assert client_ip(request, trusted_proxy_count=0) == "unknown"
