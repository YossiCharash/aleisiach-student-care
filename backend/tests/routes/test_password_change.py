from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_change_password_updates_login_credentials(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    response = api.post(
        "/auth/password/change",
        json={"current_password": "password123", "new_password": "a-fresh-pass1"},
        headers=headers,
    )
    assert response.status_code == 200

    assert (
        api.post("/auth/login", json={"username": "teacher", "password": "password123"}).status_code
        == 401
    )
    assert (
        api.post(
            "/auth/login", json={"username": "teacher", "password": "a-fresh-pass1"}
        ).status_code
        == 200
    )


def test_wrong_current_password_is_rejected(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    response = api.post(
        "/auth/password/change",
        json={"current_password": "wrong-one", "new_password": "a-fresh-pass1"},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_current_password"


def test_short_new_password_is_rejected(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    response = api.post(
        "/auth/password/change",
        json={"current_password": "password123", "new_password": "short"},
        headers=headers,
    )
    assert response.status_code == 422


def test_change_password_requires_authentication(api: TestClient) -> None:
    response = api.post(
        "/auth/password/change",
        json={"current_password": "password123", "new_password": "a-fresh-pass1"},
    )
    assert response.status_code == 401


def test_change_password_rotates_the_callers_session(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    response = api.post(
        "/auth/password/change",
        json={"current_password": "password123", "new_password": "a-fresh-pass1"},
        headers=headers,
    )
    assert response.status_code == 200

    rotated = response.json()["token"]
    assert rotated != headers["Authorization"].removeprefix("Bearer ")

    assert api.get("/students", headers=headers).status_code == 401
    assert api.get("/students", headers={"Authorization": f"Bearer {rotated}"}).status_code == 200
