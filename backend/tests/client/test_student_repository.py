import uuid

from sqlalchemy.orm import Session

from backend.app.client.students.student_repository import StudentRepository
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student


def _seed_class(session: Session) -> uuid.UUID:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    return class_entity.id


def test_add_and_get(db_session: Session) -> None:
    class_id = _seed_class(db_session)
    repository = StudentRepository(db_session)

    created = repository.add(Student(full_name="Dana", class_id=class_id))
    fetched = repository.get(created.id)

    assert fetched is not None
    assert fetched.full_name == "Dana"


def test_list_active_excludes_archived(db_session: Session) -> None:
    class_id = _seed_class(db_session)
    repository = StudentRepository(db_session)
    repository.add(Student(full_name="Active", class_id=class_id))
    repository.add(Student(full_name="Archived", class_id=class_id, is_archived=True))

    names = [student.full_name for student in repository.list_active()]

    assert names == ["Active"]
