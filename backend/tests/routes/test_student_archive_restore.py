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
SeedClass = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def test_manager_lists_archived_and_restores(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id, "Goes")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    api.post(f"/students/{student_id}/archive", headers=headers)

    archived = api.get("/students/archived", headers=headers)
    assert archived.status_code == 200
    assert [row["full_name"] for row in archived.json()] == ["Goes"]

    restored = api.post(f"/students/{student_id}/restore", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["is_archived"] is False

    assert api.get("/students/archived", headers=headers).json() == []
    assert [row["full_name"] for row in api.get("/students", headers=headers).json()] == ["Goes"]


def test_restore_is_audited_as_update(
    api: TestClient,
    db_session: Session,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id, "Goes")
    boss_id = seed_user("boss", UserRole.MANAGER).id
    headers = auth_headers(api, "boss")

    api.post(f"/students/{student_id}/archive", headers=headers)
    api.post(f"/students/{student_id}/restore", headers=headers)

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].action == AuditAction.UPDATE
    assert logs[-1].actor_id == boss_id
    assert logs[-1].entity_type == "student"


def test_restore_unknown_student_returns_404(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.post(f"/students/{uuid.uuid4()}/restore", headers=headers)
    assert response.status_code == 404


def test_archived_endpoints_are_manager_only(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id, "Goes")
    seed_user("teacher", UserRole.INSTRUCTOR, class_id=class_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)

    teacher_headers = auth_headers(api, "teacher")
    prof_headers = auth_headers(api, "prof")

    assert api.get("/students/archived", headers=teacher_headers).status_code == 403
    assert api.get("/students/archived", headers=prof_headers).status_code == 403
    assert api.post(f"/students/{student_id}/restore", headers=teacher_headers).status_code == 403


def test_archived_endpoints_require_authentication(api: TestClient) -> None:
    assert api.get("/students/archived").status_code == 401
    assert api.post(f"/students/{uuid.uuid4()}/restore").status_code == 401
