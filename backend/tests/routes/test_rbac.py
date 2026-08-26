from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]

_INVITE_BODY = {"full_name": "New User", "email": "new@example.com", "role": "instructor"}


def test_manager_can_create_invitation(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post("/auth/invitations", headers=headers, json=_INVITE_BODY)

    assert response.status_code == 201
    assert response.json()["status"] == "invited"


def test_non_manager_is_forbidden(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "teacher")

    response = api.post("/auth/invitations", headers=headers, json=_INVITE_BODY)

    assert response.status_code == 403


def test_missing_token_is_unauthorized(api: TestClient) -> None:
    response = api.post("/auth/invitations", json=_INVITE_BODY)

    assert response.status_code == 401


def test_logout_revokes_session(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    assert api.post("/auth/logout", headers=headers).status_code == 204
    after = api.post("/auth/invitations", headers=headers, json=_INVITE_BODY)
    assert after.status_code == 401
