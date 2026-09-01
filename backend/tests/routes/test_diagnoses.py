import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_creates_and_lists_diagnosis(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post("/diagnoses", headers=headers, json={"name": "אספרגר"})
    assert created.status_code == 201

    names = [row["name"] for row in api.get("/diagnoses", headers=headers).json()]
    assert "אספרגר" in names


def test_creating_existing_diagnosis_is_idempotent(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    api.post("/diagnoses", headers=headers, json={"name": "אוטיזם"})
    api.post("/diagnoses", headers=headers, json={"name": "אוטיזם"})

    names = [row["name"] for row in api.get("/diagnoses", headers=headers).json()]
    assert names.count("אוטיזם") == 1


def test_instructor_reads_but_cannot_create(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("teacher", UserRole.INSTRUCTOR)
    headers = auth_headers(api, "teacher")

    assert api.get("/diagnoses", headers=headers).status_code == 200
    forbidden = api.post("/diagnoses", headers=headers, json={"name": "x"})
    assert forbidden.status_code == 403


def test_manager_deactivates_diagnosis(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    created = api.post("/diagnoses", headers=headers, json={"name": "ישן"}).json()

    updated = api.patch(f"/diagnoses/{created['id']}", headers=headers, json={"is_active": False})
    assert updated.status_code == 200

    names = [row["name"] for row in api.get("/diagnoses", headers=headers).json()]
    assert "ישן" not in names


def test_update_unknown_diagnosis_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(f"/diagnoses/{uuid.uuid4()}", headers=headers, json={"name": "x"})
    assert response.status_code == 404


def test_readding_deactivated_diagnosis_reactivates_it(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    created = api.post("/diagnoses", headers=headers, json={"name": "חוזרת"}).json()
    api.patch(f"/diagnoses/{created['id']}", headers=headers, json={"is_active": False})

    readded = api.post("/diagnoses", headers=headers, json={"name": "חוזרת"})
    assert readded.status_code == 201
    assert readded.json()["is_active"] is True

    names = [row["name"] for row in api.get("/diagnoses", headers=headers).json()]
    assert "חוזרת" in names


def test_diagnoses_require_authentication(api: TestClient) -> None:
    assert api.get("/diagnoses").status_code == 401
