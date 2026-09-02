from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.institution import Institution
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.tests.conftest import DEFAULT_INSTITUTION_ID

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]

TENANT_PATHS = (
    "/students",
    "/classes",
    "/users",
    "/taxonomy/labels",
    "/diagnoses",
    "/detail-options",
    "/extra-section-types",
)


@pytest.fixture
def super_admin_headers(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> dict[str, str]:
    seed_user("root", UserRole.SUPER_ADMIN)
    return auth_headers(api, "root")


def test_super_admin_is_created_without_an_institution(
    seed_user: SeedUser, db_session: Session
) -> None:
    admin = seed_user("root", UserRole.SUPER_ADMIN)

    assert admin.institution_id is None


def test_super_admin_can_log_in(api: TestClient, super_admin_headers: dict[str, str]) -> None:
    assert "Authorization" in super_admin_headers


@pytest.mark.parametrize("path", TENANT_PATHS)
def test_super_admin_is_blocked_from_institution_data(
    api: TestClient, super_admin_headers: dict[str, str], path: str
) -> None:
    response = api.get(path, headers=super_admin_headers)

    assert response.status_code == 403


def test_super_admin_cannot_invite_institution_users(
    api: TestClient, super_admin_headers: dict[str, str]
) -> None:
    response = api.post(
        "/auth/invitations",
        headers=super_admin_headers,
        json={"full_name": "חדש", "email": "new@example.com", "role": "manager"},
    )

    assert response.status_code == 403


def test_institution_user_of_an_inactive_institution_is_blocked(
    api: TestClient,
    db_session: Session,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    institution = db_session.get(Institution, DEFAULT_INSTITUTION_ID)
    assert institution is not None
    institution.is_active = False
    db_session.flush()

    response = api.get("/students", headers=headers)

    assert response.status_code == 403
    assert response.json()["code"] == "institution_inactive"
