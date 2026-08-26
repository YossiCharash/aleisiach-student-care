import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_builds_taxonomy_tree(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    label = api.post("/taxonomy/labels", headers=headers, json={"name": "עצמאות"}).json()
    sub_label = api.post(
        "/taxonomy/sub-labels",
        headers=headers,
        json={"label_id": label["id"], "name": "היגיינה"},
    ).json()
    skill = api.post(
        "/taxonomy/skills",
        headers=headers,
        json={"sub_label_id": sub_label["id"], "name": "רחיצת ידיים"},
    ).json()
    api.post(
        "/taxonomy/solutions",
        headers=headers,
        json={"skill_id": skill["id"], "text": "תרגול יומי"},
    )

    tree = api.get("/taxonomy/tree", headers=headers)
    assert tree.status_code == 200
    body = tree.json()
    assert body[0]["sub_labels"][0]["skills"][0]["solutions"][0]["text"] == "תרגול יומי"


def test_instructor_can_read_but_not_write(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/taxonomy/labels", headers=headers).status_code == 200
    forbidden = api.post("/taxonomy/labels", headers=headers, json={"name": "x"})
    assert forbidden.status_code == 403


def test_reading_requires_authentication(api: TestClient) -> None:
    assert api.get("/taxonomy/tree").status_code == 401


def test_update_unknown_label_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(f"/taxonomy/labels/{uuid.uuid4()}", headers=headers, json={"name": "y"})
    assert response.status_code == 404
