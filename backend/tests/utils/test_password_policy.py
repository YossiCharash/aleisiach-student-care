from backend.app.utils.service.password_policy import PasswordPolicy


def test_accepts_password_with_letters_and_digits() -> None:
    assert PasswordPolicy().validate("password123") is None


def test_rejects_password_shorter_than_minimum() -> None:
    assert PasswordPolicy().validate("ab12") is not None


def test_rejects_password_without_digit() -> None:
    assert PasswordPolicy().validate("only-letters") is not None


def test_rejects_password_without_letter() -> None:
    assert PasswordPolicy().validate("12345678") is not None


def test_rejects_password_longer_than_maximum() -> None:
    assert PasswordPolicy().validate("a1" + "x" * 200) is not None
