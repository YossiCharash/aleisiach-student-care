from app.utils.service.token_factory import TokenFactory


def test_create_returns_raw_and_matching_hash() -> None:
    factory = TokenFactory()

    raw, token_hash = factory.create()

    assert raw
    assert token_hash == factory.hash_token(raw)
    assert factory.create()[0] != raw
