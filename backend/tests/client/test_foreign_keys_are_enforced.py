import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.client.user_session import UserSession


def test_a_row_pointing_at_a_missing_user_is_rejected(db_session: Session) -> None:
    db_session.add(
        UserSession(
            user_id=uuid.uuid4(),
            token_hash="x" * 64,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
    )

    with pytest.raises(IntegrityError):
        db_session.flush()
