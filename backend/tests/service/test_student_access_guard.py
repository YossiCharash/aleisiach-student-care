import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.students.student_access_guard import StudentAccessGuard


def _seed_student(session: Session) -> Student:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    return student


def test_require_returns_student_in_scope(db_session: Session) -> None:
    student = _seed_student(db_session)
    guard = StudentAccessGuard(StudentRepository(db_session))

    result = guard.require(student.id, StudentAccessScope(all_classes=True))

    assert result.id == student.id


def test_require_hides_student_outside_scope(db_session: Session) -> None:
    student = _seed_student(db_session)
    guard = StudentAccessGuard(StudentRepository(db_session))
    foreign = StudentAccessScope(all_classes=False, class_id=uuid.uuid4())

    with pytest.raises(NotFoundError):
        guard.require(student.id, foreign)


def test_require_raises_for_unknown_student(db_session: Session) -> None:
    guard = StudentAccessGuard(StudentRepository(db_session))

    with pytest.raises(NotFoundError):
        guard.require(uuid.uuid4(), StudentAccessScope(all_classes=True))
