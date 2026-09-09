import uuid

from sqlalchemy.orm import Session

from backend.app.client.students.student_repository import StudentRepository
from backend.app.models.client.student import Student
from backend.app.models.client.workshop import Workshop


def _seed_workshop(session: Session) -> uuid.UUID:
    workshop = Workshop(name="Aleph")
    session.add(workshop)
    session.flush()
    return workshop.id


def test_add_and_get(db_session: Session) -> None:
    workshop_id = _seed_workshop(db_session)
    repository = StudentRepository(db_session)

    created = repository.add(Student(full_name="Dana", workshop_id=workshop_id))
    fetched = repository.get(created.id)

    assert fetched is not None
    assert fetched.full_name == "Dana"


def test_list_active_excludes_archived(db_session: Session) -> None:
    workshop_id = _seed_workshop(db_session)
    repository = StudentRepository(db_session)
    repository.add(Student(full_name="Active", workshop_id=workshop_id))
    repository.add(Student(full_name="Archived", workshop_id=workshop_id, is_archived=True))

    names = [student.full_name for student in repository.list_active()]

    assert names == ["Active"]


def test_list_active_by_workshop_filters_to_one_workshop(db_session: Session) -> None:
    class_a = _seed_workshop(db_session)
    class_b = _seed_workshop(db_session)
    repository = StudentRepository(db_session)
    repository.add(Student(full_name="InA", workshop_id=class_a))
    repository.add(Student(full_name="InB", workshop_id=class_b))

    names = [student.full_name for student in repository.list_active_by_workshop(class_a)]

    assert names == ["InA"]


def test_list_archived_returns_only_archived(db_session: Session) -> None:
    workshop_id = _seed_workshop(db_session)
    repository = StudentRepository(db_session)
    repository.add(Student(full_name="Active", workshop_id=workshop_id))
    repository.add(Student(full_name="Archived", workshop_id=workshop_id, is_archived=True))

    names = [student.full_name for student in repository.list_archived()]

    assert names == ["Archived"]
