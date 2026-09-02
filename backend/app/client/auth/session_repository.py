import uuid
from datetime import datetime
from typing import Any, cast

from sqlalchemy import CursorResult, delete, select, update
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

    def revoke_all_for_user(self, user_id: uuid.UUID, revoked_at: datetime) -> None:
        self._session.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
            .execution_options(synchronize_session="fetch")
        )

    def delete_expired(self, cutoff: datetime) -> int:
        result = cast(
            CursorResult[Any],
            self._session.execute(delete(UserSession).where(UserSession.expires_at <= cutoff)),
        )
        return result.rowcount
