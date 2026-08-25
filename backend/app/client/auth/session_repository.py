from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.user_session import UserSession


class SessionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user_session: UserSession) -> UserSession:
        self._session.add(user_session)
        self._session.flush()
        return user_session

    def find_by_hash(self, token_hash: str) -> UserSession | None:
        return self._session.scalar(select(UserSession).where(UserSession.token_hash == token_hash))
