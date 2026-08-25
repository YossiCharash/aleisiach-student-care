from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.utils.service.password_hasher import PasswordHasher

_INVITE_BODY = {"full_name": "New User", "email": "new@example.com", "role": "instructor"}


def _seed_active(session: Session, username: str, role: UserRole) -> None:
    session.add(
        User(
            full_name="User",
            email=f"{username}@example.com",
            username=username,
            password_hash=PasswordHasher().hash("password123"),
            role=role,
            status=UserStatus.ACTIVE,
        )
    )
    session.flush()


def _login(api: TestClient, username: str) -> str:
    response = api.post("/auth/login", json={"username": username, "password": "password123"})
    assert response.status_code == 200
    token: str = response.json()["token"]
    return token


def test_manager_can_create_invitation(api: TestClient, db_session: Session) -> None:
    _seed_active(db_session, "boss", UserRole.MANAGER)
    headers = {"Authorization": f"Bearer {_login(api, 'boss')}"}

    response = api.post("/auth/invitations", headers=headers, json=_INVITE_BODY)

    assert response.status_code == 201
    assert response.json()["status"] == "invited"


def test_non_manager_is_forbidden(api: TestClient, db_session: Session) -> None:
    _seed_active(db_session, "teacher", UserRole.PROFESSIONAL_TEACHER)
    headers = {"Authorization": f"Bearer {_login(api, 'teacher')}"}

    response = api.post("/auth/invitations", headers=headers, json=_INVITE_BODY)

    assert response.status_code == 403


def test_missing_token_is_unauthorized(api: TestClient) -> None:
    response = api.post("/auth/invitations", json=_INVITE_BODY)

    assert response.status_code == 401


def test_logout_revokes_session(api: TestClient, db_session: Session) -> None:
    _seed_active(db_session, "boss", UserRole.MANAGER)
    headers = {"Authorization": f"Bearer {_login(api, 'boss')}"}

    assert api.post("/auth/logout", headers=headers).status_code == 204
    after = api.post("/auth/invitations", headers=headers, json=_INVITE_BODY)
    assert after.status_code == 401
