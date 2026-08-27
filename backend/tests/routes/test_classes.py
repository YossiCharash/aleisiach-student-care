import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_creates_lists_and_renames_class(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post("/classes", json={"name": "Aleph"}, headers=headers)
    assert created.status_code == 201
    class_id = created.json()["id"]

    listing = api.get("/classes", headers=headers)
    assert listing.status_code == 200
    assert [row["name"] for row in listing.json()] == ["Aleph"]

    renamed = api.patch(f"/classes/{class_id}", json={"name": "Bet"}, headers=headers)
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Bet"


def test_instructor_can_list_but_not_create(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/classes", headers=headers).status_code == 200
    assert api.post("/classes", json={"name": "Aleph"}, headers=headers).status_code == 403


def test_rename_unknown_class_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(f"/classes/{uuid.uuid4()}", json={"name": "Bet"}, headers=headers)
    assert response.status_code == 404


def test_classes_require_authentication(api: TestClient) -> None:
    assert api.get("/classes").status_code == 401
    assert api.post("/classes", json={"name": "Aleph"}).status_code == 401
