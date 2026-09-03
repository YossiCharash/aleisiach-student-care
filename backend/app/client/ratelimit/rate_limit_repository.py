from datetime import datetime
from typing import Any, cast

from sqlalchemy import CursorResult, delete, func, select
from sqlalchemy.orm import Session

from backend.app.models.client.rate_limit_hit import RateLimitHit


class RateLimitRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_since(self, bucket_key: str, threshold: datetime) -> int:
        statement = (
            select(func.count())
            .select_from(RateLimitHit)
            .where(RateLimitHit.bucket_key == bucket_key, RateLimitHit.occurred_at > threshold)
        )
        return self._session.scalar(statement) or 0

    def add(self, bucket_key: str, occurred_at: datetime) -> None:
        self._session.add(RateLimitHit(bucket_key=bucket_key, occurred_at=occurred_at))
        self._session.flush()

    def delete_before(self, cutoff: datetime) -> int:
        result = cast(
            Any,
            self._session.execute(delete(RateLimitHit).where(RateLimitHit.occurred_at <= cutoff)),
        )
        return cast(CursorResult[Any], result).rowcount
