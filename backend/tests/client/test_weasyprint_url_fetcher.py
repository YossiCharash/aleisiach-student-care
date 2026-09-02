import pytest

from backend.app.client.pdf.weasyprint_pdf_renderer import _data_only_url_fetcher


def test_non_data_uri_is_rejected() -> None:
    with pytest.raises(ValueError):
        _data_only_url_fetcher("file:///etc/passwd")


def test_remote_uri_is_rejected() -> None:
    with pytest.raises(ValueError):
        _data_only_url_fetcher("https://example.com/logo.png")


def test_data_uri_is_passed_through() -> None:
    try:
        import weasyprint  # noqa: F401
    except Exception as exc:
        pytest.skip(f"weasyprint unavailable: {exc}")

    assert _data_only_url_fetcher("data:text/plain;base64,aGVsbG8=") is not None
