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


def _build_leaf(
    api: TestClient, headers: dict[str, str]
) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    label = api.post("/taxonomy/labels", headers=headers, json={"name": "עצמאות"}).json()
    sub_label = api.post(
        "/taxonomy/sub-labels", headers=headers, json={"label_id": label["id"], "name": "היגיינה"}
    ).json()
    skill = api.post(
        "/taxonomy/skills",
        headers=headers,
        json={"sub_label_id": sub_label["id"], "name": "רחיצת ידיים"},
    ).json()
    solution = api.post(
        "/taxonomy/solutions", headers=headers, json={"skill_id": skill["id"], "text": "תרגול יומי"}
    ).json()
    return label, sub_label, skill, solution


def test_deactivated_children_are_listable_and_reactivatable(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    label, sub_label, skill, solution = _build_leaf(api, headers)

    for path in (
        f"/taxonomy/sub-labels/{sub_label['id']}",
        f"/taxonomy/skills/{skill['id']}",
        f"/taxonomy/solutions/{solution['id']}",
    ):
        assert api.patch(path, headers=headers, json={"is_active": False}).status_code == 200

    subs = f"/taxonomy/sub-labels?label_id={label['id']}"
    skills = f"/taxonomy/skills?sub_label_id={sub_label['id']}"
    solutions = f"/taxonomy/solutions?skill_id={skill['id']}"

    assert api.get(subs, headers=headers).json() == []
    assert api.get(skills, headers=headers).json() == []
    assert api.get(solutions, headers=headers).json() == []

    assert len(api.get(f"{subs}&include_inactive=true", headers=headers).json()) == 1
    assert len(api.get(f"{skills}&include_inactive=true", headers=headers).json()) == 1
    assert len(api.get(f"{solutions}&include_inactive=true", headers=headers).json()) == 1

    assert (
        api.patch(
            f"/taxonomy/sub-labels/{sub_label['id']}", headers=headers, json={"is_active": True}
        ).status_code
        == 200
    )
    assert len(api.get(subs, headers=headers).json()) == 1


def test_list_children_of_unknown_parent_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    missing = uuid.uuid4()

    assert api.get(f"/taxonomy/sub-labels?label_id={missing}", headers=headers).status_code == 404
    assert api.get(f"/taxonomy/skills?sub_label_id={missing}", headers=headers).status_code == 404
    assert api.get(f"/taxonomy/solutions?skill_id={missing}", headers=headers).status_code == 404


def test_listing_children_requires_authentication(api: TestClient) -> None:
    assert api.get(f"/taxonomy/sub-labels?label_id={uuid.uuid4()}").status_code == 401
    assert api.get(f"/taxonomy/skills?sub_label_id={uuid.uuid4()}").status_code == 401
    assert api.get(f"/taxonomy/solutions?skill_id={uuid.uuid4()}").status_code == 401
