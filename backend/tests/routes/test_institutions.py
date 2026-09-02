import uuid
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]

NEW_INSTITUTION = {
    "name": "בית ספר חדש",
    "code": "new-school",
    "manager_full_name": "מנהלת חדשה",
    "manager_email": "principal@example.org",
}


@pytest.fixture
def admin_headers(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> dict[str, str]:
    seed_user("root", UserRole.SUPER_ADMIN)
    return auth_headers(api, "root")


def test_super_admin_lists_institutions_with_counts(
    api: TestClient, admin_headers: dict[str, str], seed_user: SeedUser
) -> None:
    seed_user("boss", UserRole.MANAGER)

    response = api.get("/institutions", headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["code"] for item in body] == ["test"]
    assert body[0]["user_count"] == 1
    assert body[0]["student_count"] == 0


def test_creating_an_institution_returns_it_as_active(
    api: TestClient, admin_headers: dict[str, str]
) -> None:
    response = api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION)

    assert response.status_code == 201
    assert response.json()["name"] == "בית ספר חדש"
    assert response.json()["is_active"] is True


def test_creating_an_institution_invites_its_first_manager(
    api: TestClient, admin_headers: dict[str, str], db_session: Session
) -> None:
    created = api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION)

    with TenantBinding.platform(db_session):
        manager = db_session.scalars(
            select(User).where(User.email == NEW_INSTITUTION["manager_email"])
        ).one()
    assert manager.role == UserRole.MANAGER
    assert manager.status == UserStatus.INVITED
    assert str(manager.institution_id) == created.json()["id"]


def test_creating_an_institution_seeds_its_detail_options(
    api: TestClient, admin_headers: dict[str, str], db_session: Session
) -> None:
    created = api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION)
    institution_id = uuid.UUID(created.json()["id"])

    with TenantBinding.platform(db_session):
        options = db_session.scalars(
            select(DetailOption).where(DetailOption.institution_id == institution_id)
        ).all()

    assert [option.name for option in options if option.field.value == "idd_severity"] == [
        "קלה",
        "בינונית",
        "מורכבת",
    ]


def test_duplicate_code_is_rejected(api: TestClient, admin_headers: dict[str, str]) -> None:
    api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION)

    response = api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION)

    assert response.status_code == 409
    assert response.json()["code"] == "institution_code_taken"


def test_code_must_be_url_safe(api: TestClient, admin_headers: dict[str, str]) -> None:
    response = api.post(
        "/institutions", headers=admin_headers, json={**NEW_INSTITUTION, "code": "בית ספר"}
    )

    assert response.status_code == 422


def test_institution_can_be_renamed(api: TestClient, admin_headers: dict[str, str]) -> None:
    created = api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION).json()

    response = api.patch(
        f"/institutions/{created['id']}", headers=admin_headers, json={"name": "שם מעודכן"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "שם מעודכן"


def test_institution_can_be_deactivated_and_reactivated(
    api: TestClient, admin_headers: dict[str, str]
) -> None:
    created = api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION).json()

    deactivated = api.post(
        f"/institutions/{created['id']}/deactivate", headers=admin_headers
    ).json()
    reactivated = api.post(f"/institutions/{created['id']}/activate", headers=admin_headers).json()

    assert deactivated["is_active"] is False
    assert reactivated["is_active"] is True


def test_unknown_institution_is_not_found(api: TestClient, admin_headers: dict[str, str]) -> None:
    response = api.get("/institutions/11111111-2222-3333-4444-555555555555", headers=admin_headers)

    assert response.status_code == 404


def test_institution_manager_cannot_reach_the_console(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    assert api.get("/institutions", headers=headers).status_code == 403
    assert api.post("/institutions", headers=headers, json=NEW_INSTITUTION).status_code == 403


def test_console_requires_authentication(api: TestClient) -> None:
    assert api.get("/institutions").status_code == 401


def test_new_institution_starts_without_students_or_taxonomy(
    api: TestClient, admin_headers: dict[str, str]
) -> None:
    api.post("/institutions", headers=admin_headers, json=NEW_INSTITUTION)

    listed = api.get("/institutions", headers=admin_headers).json()
    created = [item for item in listed if item["code"] == "new-school"][0]

    assert created["student_count"] == 0
    assert created["user_count"] == 1
