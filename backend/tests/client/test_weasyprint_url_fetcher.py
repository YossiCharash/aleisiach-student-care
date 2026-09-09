import pytest

from backend.app.client.pdf.url_fetcher import UrlFetcher
from backend.app.client.pdf.weasyprint_pdf_renderer import build_data_only_url_fetcher

try:
    import weasyprint  # noqa: F401
except Exception as exc:
    pytest.skip(f"weasyprint unavailable: {exc}", allow_module_level=True)


def fetcher() -> UrlFetcher:
    return build_data_only_url_fetcher()


def test_non_data_uri_is_rejected() -> None:
    with pytest.raises(ValueError):
        fetcher().fetch("file:///etc/passwd")


def test_remote_uri_is_rejected() -> None:
    with pytest.raises(ValueError):
        fetcher().fetch("https://example.com/logo.png")


def test_data_uri_is_passed_through() -> None:
    assert fetcher().fetch("data:text/plain;base64,aGVsbG8=") is not None
