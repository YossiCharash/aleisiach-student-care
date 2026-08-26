import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_lists_and_disables_user(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    target = seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "boss")

    listing = api.get("/users", headers=headers)
    assert listing.status_code == 200
    assert {row["username"] for row in listing.json()} == {"boss", "teacher"}

    disabled = api.post(f"/users/{target.id}/disable", headers=headers)
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "disabled"

    denied = api.post("/auth/login", json={"username": "teacher", "password": "password123"})
    assert denied.status_code == 401


def test_disabled_user_session_is_rejected(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    target = seed_user("teacher", UserRole.INSTRUCTOR)
    teacher_headers = auth_headers(api, "teacher")
    assert api.get("/students", headers=teacher_headers).status_code == 200

    api.post(f"/users/{target.id}/disable", headers=auth_headers(api, "boss"))

    assert api.get("/students", headers=teacher_headers).status_code == 401


def test_manager_cannot_disable_self(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    boss = seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/users/{boss.id}/disable", headers=headers)
    assert response.status_code == 400
    assert response.json()["code"] == "cannot_disable_self"


def test_non_manager_is_forbidden(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/users", headers=headers).status_code == 403


def test_users_require_authentication(api: TestClient) -> None:
    assert api.get("/users").status_code == 401
    assert api.post(f"/users/{uuid.uuid4()}/disable").status_code == 401
