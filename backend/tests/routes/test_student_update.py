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


def test_manager_renames_student_and_moves_class(
    api: TestClient,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    origin_id = seed_class("Aleph")
    target_id = seed_class("Bet")
    student_id = seed_student(origin_id, "Typo")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/students/{student_id}",
        json={"full_name": "Fixed", "class_id": str(target_id)},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Fixed"
    assert response.json()["class_id"] == str(target_id)


def test_update_records_only_changed_fields_in_audit(
    api: TestClient,
    db_session: Session,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id, "Typo")
    boss_id = seed_user("boss", UserRole.MANAGER).id
    headers = auth_headers(api, "boss")

    api.patch(
        f"/students/{student_id}",
        json={"full_name": "Fixed", "class_id": str(class_id)},
        headers=headers,
    )

    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].action == AuditAction.UPDATE
    assert logs[-1].actor_id == boss_id
    assert logs[-1].entity_type == "student"
    assert logs[-1].changes == ["full_name"]


def test_update_without_changes_is_not_audited(
    api: TestClient,
    db_session: Session,
    seed_class: SeedClass,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    student_id = seed_student(class_id, "Same")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    before = len(list(db_session.scalars(select(AuditLog))))
    api.patch(
        f"/students/{student_id}",
        json={"full_name": "Same", "class_id": str(class_id)},
        headers=headers,
    )

    assert len(list(db_session.scalars(select(AuditLog)))) == before


def test_update_rejects_unknown_class(
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

    response = api.patch(
        f"/students/{student_id}",
        json={"full_name": "Goes", "class_id": str(uuid.uuid4())},
        headers=headers,
    )

    assert response.status_code == 404


def test_update_unknown_student_returns_404(
    api: TestClient,
    seed_class: SeedClass,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_id = seed_class("Aleph")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    response = api.patch(
        f"/students/{uuid.uuid4()}",
        json={"full_name": "Ghost", "class_id": str(class_id)},
        headers=headers,
    )

    assert response.status_code == 404


def test_update_rejects_blank_name(
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

    response = api.patch(
        f"/students/{student_id}",
        json={"full_name": "", "class_id": str(class_id)},
        headers=headers,
    )

    assert response.status_code == 422


def test_update_is_manager_only(
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
    payload = {"full_name": "Hacked", "class_id": str(class_id)}

    teacher = api.patch(
        f"/students/{student_id}", json=payload, headers=auth_headers(api, "teacher")
    )
    prof = api.patch(f"/students/{student_id}", json=payload, headers=auth_headers(api, "prof"))

    assert teacher.status_code == 403
    assert prof.status_code == 403


def test_update_requires_authentication(api: TestClient) -> None:
    response = api.patch(
        f"/students/{uuid.uuid4()}",
        json={"full_name": "Anon", "class_id": str(uuid.uuid4())},
    )
    assert response.status_code == 401
