from datetime import date

from backend.app.utils.service.clock import Clock


def test_today_returns_a_date() -> None:
    assert isinstance(Clock().today(), date)


def test_now_is_timezone_aware() -> None:
    assert Clock().now().tzinfo is not None
