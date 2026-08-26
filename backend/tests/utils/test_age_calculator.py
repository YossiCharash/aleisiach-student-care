from datetime import date

from backend.app.utils.service.age_calculator import AgeCalculator


def test_age_before_birthday_this_year() -> None:
    assert AgeCalculator.age_in_years(date(2010, 12, 31), date(2026, 8, 26)) == 15


def test_age_after_birthday_this_year() -> None:
    assert AgeCalculator.age_in_years(date(2010, 1, 1), date(2026, 8, 26)) == 16


def test_age_on_birthday() -> None:
    assert AgeCalculator.age_in_years(date(2010, 8, 26), date(2026, 8, 26)) == 16
