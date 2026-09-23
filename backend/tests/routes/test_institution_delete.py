import uuid
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.institution import Institution
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedInstitution = Callable[..., Institution]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


@pytest.fixture
def admin_headers(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> dict[str, str]:
    seed_user("root", UserRole.SUPER_ADMIN)
    return auth_headers(api, "root")


def _delete(
    api: TestClient, institution_id: uuid.UUID, password: str, headers: dict[str, str]
) -> Response:
    return api.request(
        "DELETE", f"/institutions/{institution_id}", json={"password": password}, headers=headers
    )


def test_super_admin_deletes_institution_with_correct_password(
    api: TestClient,
    admin_headers: dict[str, str],
    seed_institution: SeedInstitution,
    seed_user: SeedUser,
    db_session: Session,
) -> None:
    target = seed_institution("בית ספר ב", "school-b")
    target_id = target.id
    member_id = seed_user("member", UserRole.MANAGER, institution_id=target_id).id

    response = _delete(api, target_id, "password123", admin_headers)

    assert response.status_code == 204
    assert api.get(f"/institutions/{target_id}", headers=admin_headers).status_code == 404
    with TenantBinding.platform(db_session):
        assert db_session.get(Institution, target_id) is None
        assert db_session.get(User, member_id) is None


def test_wrong_password_keeps_the_institution(
    api: TestClient,
    admin_headers: dict[str, str],
    seed_institution: SeedInstitution,
) -> None:
    target_id = seed_institution("בית ספר ב", "school-b").id
    assert api.get(f"/institutions/{target_id}", headers=admin_headers).status_code == 200

    response = _delete(api, target_id, "nope", admin_headers)

    assert response.status_code == 400
    assert api.get(f"/institutions/{target_id}", headers=admin_headers).status_code == 200


def test_managers_cannot_delete_institutions(
    api: TestClient,
    seed_institution: SeedInstitution,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    target = seed_institution("בית ספר ב", "school-b")
    seed_user("boss", UserRole.MANAGER)

    response = _delete(api, target.id, "password123", auth_headers(api, "boss"))

    assert response.status_code == 403


def test_deleting_unknown_institution_returns_404(
    api: TestClient, admin_headers: dict[str, str]
) -> None:
    response = _delete(api, uuid.uuid4(), "password123", admin_headers)

    assert response.status_code == 404
