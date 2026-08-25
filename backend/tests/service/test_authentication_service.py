import pytest
from app.client.users.user_repository import UserRepository
from app.errors.service.authentication_error import AuthenticationError
from app.models.client.user import User
from app.models.client.user_role import UserRole
from app.models.client.user_status import UserStatus
from app.service.auth.authentication_service import AuthenticationService
from app.utils.service.password_hasher import PasswordHasher
from sqlalchemy.orm import Session


def _seed_active_user(session: Session, hasher: PasswordHasher) -> None:
    session.add(
        User(
            full_name="Manager",
            email="m@example.com",
            username="manager1",
            password_hash=hasher.hash("password123"),
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE,
        )
    )
    session.flush()


def test_authenticate_success(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = AuthenticationService(UserRepository(db_session), hasher)

    result = service.authenticate("manager1", "password123")

    assert result.username == "manager1"


def test_authenticate_wrong_password_raises(db_session: Session) -> None:
    hasher = PasswordHasher()
    _seed_active_user(db_session, hasher)
    service = AuthenticationService(UserRepository(db_session), hasher)

    with pytest.raises(AuthenticationError):
        service.authenticate("manager1", "wrong-password")


def test_authenticate_unknown_user_raises(db_session: Session) -> None:
    service = AuthenticationService(UserRepository(db_session), PasswordHasher())

    with pytest.raises(AuthenticationError):
        service.authenticate("ghost", "password123")
