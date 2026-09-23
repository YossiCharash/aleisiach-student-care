import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.password_verifier import PasswordVerifier
from backend.tests.conftest import DEFAULT_INSTITUTION_ID


def _verifier(session: Session) -> PasswordVerifier:
    return PasswordVerifier(UserRepository(session), PasswordHasher())


def _seed_actor(session: Session) -> uuid.UUID:
    user = User(
        full_name="Boss",
        email="boss@example.com",
        username="boss",
        password_hash=PasswordHasher().hash("password123"),
        role=UserRole.MANAGER,
        institution_id=DEFAULT_INSTITUTION_ID,
    )
    session.add(user)
    session.flush()
    return user.id


def test_accepts_the_correct_password(db_session: Session) -> None:
    actor_id = _seed_actor(db_session)
    _verifier(db_session).verify(actor_id, "password123")


def test_rejects_a_wrong_password(db_session: Session) -> None:
    actor_id = _seed_actor(db_session)
    with pytest.raises(InvalidCurrentPasswordError):
        _verifier(db_session).verify(actor_id, "nope")


def test_rejects_an_unknown_actor(db_session: Session) -> None:
    with pytest.raises(AuthenticationError):
        _verifier(db_session).verify(uuid.uuid4(), "password123")
