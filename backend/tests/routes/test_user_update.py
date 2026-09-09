import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]


def test_manager_updates_name_and_email(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    origin_id = seed_workshop("Aleph")
    teacher_id = seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=origin_id).id
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/users/{teacher_id}",
        json={
            "full_name": "Fixed Name",
            "email": "fixed@example.com",
            "role": UserRole.INSTRUCTOR.value,
        },
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Fixed Name"
    assert body["email"] == "fixed@example.com"
    assert body["workshop_id"] == str(origin_id)


def test_promoting_instructor_to_manager_clears_workshop(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    teacher_id = seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id).id
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/users/{teacher_id}",
        json={
            "full_name": "User",
            "email": "teacher@example.com",
            "role": UserRole.MANAGER.value,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["workshop_id"] is None


def test_manager_cannot_change_own_role(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    boss_id = seed_user("boss", UserRole.MANAGER).id
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/users/{boss_id}",
        json={
            "full_name": "User",
            "email": "boss@example.com",
            "role": UserRole.PROFESSIONAL_TEACHER.value,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["code"] == "cannot_change_own_role"


def test_manager_may_still_fix_own_name(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    boss_id = seed_user("boss", UserRole.MANAGER).id
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/users/{boss_id}",
        json={
            "full_name": "Real Name",
            "email": "boss@example.com",
            "role": UserRole.MANAGER.value,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Real Name"


def test_email_taken_by_another_user_is_rejected(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    prof_id = seed_user("prof", UserRole.PROFESSIONAL_TEACHER).id
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/users/{prof_id}",
        json={
            "full_name": "User",
            "email": "boss@example.com",
            "role": UserRole.PROFESSIONAL_TEACHER.value,
        },
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "email_already_used"


def test_update_records_only_changed_fields_in_audit(
    api: TestClient,
    db_session: Session,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    prof_id = seed_user("prof", UserRole.PROFESSIONAL_TEACHER).id
    boss_id = seed_user("boss", UserRole.MANAGER).id
    headers = auth_headers(api, "boss")

    api.patch(
        f"/users/{prof_id}",
        json={
            "full_name": "Renamed",
            "email": "prof@example.com",
            "role": UserRole.PROFESSIONAL_TEACHER.value,
        },
        headers=headers,
    )

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].action == AuditAction.UPDATE
    assert logs[-1].actor_id == boss_id
    assert logs[-1].entity_type == "user"
    assert logs[-1].changes == ["full_name"]


def test_unknown_user_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/users/{uuid.uuid4()}",
        json={
            "full_name": "Ghost",
            "email": "ghost@example.com",
            "role": UserRole.MANAGER.value,
        },
        headers=headers,
    )

    assert response.status_code == 404


def test_update_is_manager_only(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    teacher = seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    payload = {
        "full_name": "Hacked",
        "email": "hacked@example.com",
        "role": UserRole.MANAGER.value,
    }

    by_teacher = api.patch(
        f"/users/{teacher.id}", json=payload, headers=auth_headers(api, "teacher")
    )
    by_prof = api.patch(f"/users/{teacher.id}", json=payload, headers=auth_headers(api, "prof"))

    assert by_teacher.status_code == 403
    assert by_prof.status_code == 403


def test_update_requires_authentication(api: TestClient) -> None:
    response = api.patch(
        f"/users/{uuid.uuid4()}",
        json={
            "full_name": "Anon",
            "email": "anon@example.com",
            "role": UserRole.MANAGER.value,
        },
    )
    assert response.status_code == 401
