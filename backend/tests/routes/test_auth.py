from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.auth_token import AuthToken
from backend.app.models.client.token_kind import TokenKind
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.token_factory import TokenFactory
from backend.tests.conftest import DEFAULT_INSTITUTION_ID


def _seed_invited_user(session: Session) -> str:
    user = User(
        full_name="Manager",
        email="m@example.com",
        role=UserRole.MANAGER,
        status=UserStatus.INVITED,
        institution_id=DEFAULT_INSTITUTION_ID,
    )
    session.add(user)
    session.flush()
    raw, token_hash = TokenFactory().create()
    session.add(
        AuthToken(
            user_id=user.id,
            kind=TokenKind.INVITE,
            token_hash=token_hash,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
    )
    session.flush()
    return raw


def test_accept_invitation_then_login(api: TestClient, db_session: Session) -> None:
    raw_token = _seed_invited_user(db_session)

    accepted = api.post(
        "/auth/invitations/accept",
        json={"token": raw_token, "username": "manager1", "password": "manager-pass-2026"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "active"

    ok = api.post("/auth/login", json={"username": "manager1", "password": "manager-pass-2026"})
    assert ok.status_code == 200
    assert ok.json()["token"]
    assert ok.json()["user"]["username"] == "manager1"

    bad = api.post("/auth/login", json={"username": "manager1", "password": "nope"})
    assert bad.status_code == 401


def test_accept_with_invalid_token_returns_400(api: TestClient) -> None:
    response = api.post(
        "/auth/invitations/accept",
        json={"token": "invalid", "username": "someone", "password": "manager-pass-2026"},
    )
    assert response.status_code == 400


def test_password_reset_request_is_neutral(api: TestClient) -> None:
    response = api.post("/auth/password-reset/request", json={"email": "nobody@example.com"})
    assert response.status_code == 202


def test_login_seeded_active_user(api: TestClient, db_session: Session) -> None:
    hasher = PasswordHasher()
    db_session.add(
        User(
            full_name="Prof",
            email="p@example.com",
            username="prof1",
            password_hash=hasher.hash("password123"),
            role=UserRole.PROFESSIONAL_TEACHER,
            status=UserStatus.ACTIVE,
            institution_id=DEFAULT_INSTITUTION_ID,
        )
    )
    db_session.flush()

    response = api.post("/auth/login", json={"username": "prof1", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "professional_teacher"
