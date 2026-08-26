import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails


def _seed_student(session: Session) -> uuid.UUID:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    return student.id


def test_get_or_create_inserts_when_absent(db_session: Session) -> None:
    student_id = _seed_student(db_session)
    repository = StudentDetailsRepository(db_session)

    details, created = repository.get_or_create(student_id)

    assert details.student_id == student_id
    assert created is True


def test_get_or_create_returns_existing_without_duplicate(db_session: Session) -> None:
    student_id = _seed_student(db_session)
    repository = StudentDetailsRepository(db_session)
    repository.get_or_create(student_id)

    again, created = repository.get_or_create(student_id)

    assert again.student_id == student_id
    assert created is False
    count = db_session.scalar(
        select(func.count())
        .select_from(StudentDetails)
        .where(StudentDetails.student_id == student_id)
    )
    assert count == 1
