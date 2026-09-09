import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]

_COLOR = "#3F8420"


def test_manager_creates_lists_and_updates_workshop(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post("/workshops", json={"name": "Aleph", "color": _COLOR}, headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert body["color"] == _COLOR
    assert body["instructor_id"] is None
    workshop_id = body["id"]

    listing = api.get("/workshops", headers=headers)
    assert listing.status_code == 200
    assert [row["name"] for row in listing.json()] == ["Aleph"]

    updated = api.patch(
        f"/workshops/{workshop_id}",
        json={"name": "Bet", "color": "#85C441"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Bet"
    assert updated.json()["color"] == "#85C441"


def test_manager_assigns_an_instructor_to_the_workshop(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    teacher = seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "boss")

    created = api.post(
        "/workshops",
        json={"name": "Aleph", "color": _COLOR, "instructor_id": str(teacher.id)},
        headers=headers,
    )
    assert created.status_code == 201
    assert created.json()["instructor_id"] == str(teacher.id)
    assert created.json()["instructor_name"] == teacher.full_name


def test_create_rejects_an_invalid_color(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post("/workshops", json={"name": "Aleph", "color": "green"}, headers=headers)
    assert response.status_code == 422


def test_instructor_can_list_but_not_create(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/workshops", headers=headers).status_code == 200
    assert (
        api.post("/workshops", json={"name": "Aleph", "color": _COLOR}, headers=headers).status_code
        == 403
    )


def test_update_unknown_workshop_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/workshops/{uuid.uuid4()}", json={"name": "Bet", "color": _COLOR}, headers=headers
    )
    assert response.status_code == 404


def test_workshops_require_authentication(api: TestClient) -> None:
    assert api.get("/workshops").status_code == 401
    assert api.post("/workshops", json={"name": "Aleph", "color": _COLOR}).status_code == 401
