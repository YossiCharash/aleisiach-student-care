import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_adds_and_lists_option(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post(
        "/detail-options",
        headers=headers,
        json={"field": "expression_mode", "name": "שפת סימנים"},
    )
    assert created.status_code == 201
    assert created.json()["field"] == "expression_mode"

    options = api.get("/detail-options", headers=headers).json()
    names = [row["name"] for row in options if row["field"] == "expression_mode"]
    assert "שפת סימנים" in names


def test_duplicate_option_is_idempotent(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    api.post("/detail-options", headers=headers, json={"field": "idd_severity", "name": "עמוקה"})
    api.post("/detail-options", headers=headers, json={"field": "idd_severity", "name": "עמוקה"})

    options = api.get("/detail-options", headers=headers).json()
    names = [row["name"] for row in options if row["field"] == "idd_severity"]
    assert names.count("עמוקה") == 1


def test_same_name_allowed_across_fields(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    first = api.post(
        "/detail-options", headers=headers, json={"field": "idd_severity", "name": "אחר"}
    )
    second = api.post(
        "/detail-options", headers=headers, json={"field": "assistive_device", "name": "אחר"}
    )
    assert first.status_code == 201
    assert second.status_code == 201


def test_instructor_reads_but_cannot_create(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/detail-options", headers=headers).status_code == 200
    forbidden = api.post(
        "/detail-options", headers=headers, json={"field": "idd_severity", "name": "x"}
    )
    assert forbidden.status_code == 403


def test_manager_deactivates_option(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    created = api.post(
        "/detail-options",
        headers=headers,
        json={"field": "language_comprehension", "name": "ישן"},
    ).json()

    updated = api.patch(
        f"/detail-options/{created['id']}", headers=headers, json={"is_active": False}
    )
    assert updated.status_code == 200

    active = [row["name"] for row in api.get("/detail-options", headers=headers).json()]
    assert "ישן" not in active


def test_unknown_field_is_rejected(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post("/detail-options", headers=headers, json={"field": "nonsense", "name": "x"})
    assert response.status_code == 422


def test_update_unknown_option_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(f"/detail-options/{uuid.uuid4()}", headers=headers, json={"name": "x"})
    assert response.status_code == 404


def test_readding_deactivated_option_reactivates_it(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    created = api.post(
        "/detail-options", headers=headers, json={"field": "idd_severity", "name": "חוזרת"}
    ).json()
    api.patch(f"/detail-options/{created['id']}", headers=headers, json={"is_active": False})

    readded = api.post(
        "/detail-options", headers=headers, json={"field": "idd_severity", "name": "חוזרת"}
    )
    assert readded.status_code == 201
    assert readded.json()["is_active"] is True

    active = [row["name"] for row in api.get("/detail-options", headers=headers).json()]
    assert "חוזרת" in active


def test_detail_options_require_authentication(api: TestClient) -> None:
    assert api.get("/detail-options").status_code == 401
