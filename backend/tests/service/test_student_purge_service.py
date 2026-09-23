import uuid
from collections.abc import Callable

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.audit.audit_log_repository import AuditLogRepository
from backend.app.client.students.student_purge_repository import StudentPurgeRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.audit_log import AuditLog
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.student_purge_service import StudentPurgeService
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.password_verifier import PasswordVerifier

SeedUser = Callable[..., User]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]


def _service(session: Session) -> StudentPurgeService:
    return StudentPurgeService(
        StudentRepository(session),
        StudentPurgeRepository(session),
        PasswordVerifier(UserRepository(session), PasswordHasher()),
        AuditLogger(AuditLogRepository(session)),
    )


def test_deletes_the_student_and_records_an_audit_entry(
    db_session: Session,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, "Dana")
    actor_id = seed_user("boss", UserRole.MANAGER).id

    _service(db_session).delete(student_id, actor_id, "password123")

    assert db_session.get(Student, student_id) is None
    logs = list(db_session.scalars(select(AuditLog).order_by(AuditLog.created_at)))
    assert logs[-1].action == AuditAction.DELETE
    assert logs[-1].entity_id == student_id


def test_wrong_password_raises_and_keeps_the_student(
    db_session: Session,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, "Dana")
    actor_id = seed_user("boss", UserRole.MANAGER).id

    with pytest.raises(InvalidCurrentPasswordError):
        _service(db_session).delete(student_id, actor_id, "nope")

    assert db_session.get(Student, student_id) is not None


def test_unknown_student_raises_not_found(db_session: Session, seed_user: SeedUser) -> None:
    actor_id = seed_user("boss", UserRole.MANAGER).id

    with pytest.raises(NotFoundError):
        _service(db_session).delete(uuid.uuid4(), actor_id, "password123")
