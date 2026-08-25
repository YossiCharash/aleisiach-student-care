from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.auth_token import AuthToken


class AuthTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, token: AuthToken) -> AuthToken:
        self._session.add(token)
        self._session.flush()
        return token

    def find_by_hash(self, token_hash: str) -> AuthToken | None:
        return self._session.scalar(select(AuthToken).where(AuthToken.token_hash == token_hash))
