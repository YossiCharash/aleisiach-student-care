import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def _delete(
    api: TestClient, student_id: uuid.UUID, password: str, headers: dict[str, str]
) -> Response:
    return api.request(
        "DELETE", f"/students/{student_id}", json={"password": password}, headers=headers
    )


def test_manager_permanently_deletes_student_with_correct_password(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, "Dana")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = _delete(api, student_id, "password123", headers)

    assert response.status_code == 204
    assert api.get(f"/students/{student_id}", headers=headers).status_code == 404


def test_wrong_password_keeps_the_student(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, "Dana")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = _delete(api, student_id, "wrong-password", headers)

    assert response.status_code == 400
    assert api.get(f"/students/{student_id}", headers=headers).status_code == 200


def test_deletion_is_audited(
    api: TestClient,
    db_session: Session,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, "Dana")
    boss_id = seed_user("boss", UserRole.MANAGER).id
    headers = auth_headers(api, "boss")

    _delete(api, student_id, "password123", headers)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].action == AuditAction.DELETE
    assert logs[-1].actor_id == boss_id
    assert logs[-1].entity_type == "student"
    assert logs[-1].entity_id == student_id


def test_non_managers_cannot_delete(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, "Dana")
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)

    teacher = _delete(api, student_id, "password123", auth_headers(api, "teacher"))
    prof = _delete(api, student_id, "password123", auth_headers(api, "prof"))

    assert teacher.status_code == 403
    assert prof.status_code == 403


def test_deleting_unknown_student_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = _delete(api, uuid.uuid4(), "password123", headers)

    assert response.status_code == 404
