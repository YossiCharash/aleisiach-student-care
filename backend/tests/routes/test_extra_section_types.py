from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_builds_heading_tree(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    heading = api.post("/extra-section-types", headers=headers, json={"name": "העדפות"}).json()
    api.post(
        "/extra-section-types",
        headers=headers,
        json={"name": "רגישויות", "parent_id": heading["id"]},
    )

    tree = api.get("/extra-section-types/tree", headers=headers)
    assert tree.status_code == 200
    body = tree.json()
    assert body[0]["name"] == "העדפות"
    assert body[0]["children"][0]["name"] == "רגישויות"


def test_sub_heading_cannot_be_nested(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    heading = api.post("/extra-section-types", headers=headers, json={"name": "כותרת"}).json()
    sub = api.post(
        "/extra-section-types",
        headers=headers,
        json={"name": "תת", "parent_id": heading["id"]},
    ).json()

    nested = api.post(
        "/extra-section-types",
        headers=headers,
        json={"name": "עמוק", "parent_id": sub["id"]},
    )
    assert nested.status_code == 400
    assert nested.json()["code"] == "invalid_section_type"


def test_instructor_reads_but_cannot_write_types(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/extra-section-types", headers=headers).status_code == 200
    forbidden = api.post("/extra-section-types", headers=headers, json={"name": "x"})
    assert forbidden.status_code == 403


def test_types_require_authentication(api: TestClient) -> None:
    assert api.get("/extra-section-types/tree").status_code == 401
