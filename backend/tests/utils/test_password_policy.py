from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.utils.service.password_policy import PasswordPolicy


def _policy() -> PasswordPolicy:
    settings = AuthSettings()
    return PasswordPolicy(settings.password_min_length, settings.password_max_length)


def test_accepts_password_with_letters_and_digits() -> None:
    assert _policy().validate("password123") is None


def test_rejects_password_shorter_than_minimum() -> None:
    assert _policy().validate("ab12") is not None


def test_rejects_password_without_digit() -> None:
    assert _policy().validate("only-letters") is not None


def test_accepts_password_made_only_of_digits() -> None:
    assert _policy().validate("12345678") is None


def test_accepts_password_without_an_uppercase_letter() -> None:
    assert _policy().validate("all-lowercase-1") is None


def test_rejects_password_longer_than_maximum() -> None:
    assert _policy().validate("a1" + "x" * 200) is not None
