from backend.app.utils.service.password_hasher import PasswordHasher


def test_hash_is_not_plaintext_and_verifies() -> None:
    hasher = PasswordHasher()

    hashed = hasher.hash("secret-password")

    assert hashed != "secret-password"
    assert hasher.verify(hashed, "secret-password") is True
    assert hasher.verify(hashed, "wrong-password") is False
