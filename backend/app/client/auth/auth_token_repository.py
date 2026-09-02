import uuid
from datetime import datetime
from typing import Any, cast

from sqlalchemy import CursorResult, delete, select, update
from sqlalchemy.orm import Session

from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.token_kind import TokenKind


class AuthTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, token: AuthToken) -> AuthToken:
        self._session.add(token)
        self._session.flush()
        return token

    def find_by_hash(self, token_hash: str) -> AuthToken | None:
        return self._session.scalar(select(AuthToken).where(AuthToken.token_hash == token_hash))

    def invalidate_pending(self, user_id: uuid.UUID, kind: TokenKind, used_at: datetime) -> None:
        self._session.execute(
            update(AuthToken)
            .where(
                AuthToken.user_id == user_id,
                AuthToken.kind == kind,
                AuthToken.used_at.is_(None),
            )
            .values(used_at=used_at)
            .execution_options(synchronize_session="fetch")
        )

    def delete_expired(self, cutoff: datetime) -> int:
        result = cast(
            CursorResult[Any],
            self._session.execute(delete(AuthToken).where(AuthToken.expires_at <= cutoff)),
        )
        return result.rowcount
