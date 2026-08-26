import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.notes.social_note_repository import SocialNoteRepository
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.social_note import SocialNote
from backend.app.models.client.student import Student


def _seed_student(session: Session) -> uuid.UUID:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name="Dana", class_id=class_entity.id)
    session.add(student)
    session.flush()
    return student.id


def _note(student_id: uuid.UUID) -> SocialNote:
    return SocialNote(
        student_id=student_id,
        content="note",
        updated_by=uuid.uuid4(),
        updated_at=datetime.now(UTC),
    )


def test_create_inserts_when_absent(db_session: Session) -> None:
    student_id = _seed_student(db_session)
    repository = SocialNoteRepository(db_session)

    note, created = repository.create(_note(student_id))

    assert created is True
    assert note.student_id == student_id


def test_create_returns_existing_on_conflict(db_session: Session) -> None:
    student_id = _seed_student(db_session)
    repository = SocialNoteRepository(db_session)
    repository.create(_note(student_id))

    again, created = repository.create(_note(student_id))

    assert created is False
    assert again.student_id == student_id
    count = db_session.scalar(
        select(func.count()).select_from(SocialNote).where(SocialNote.student_id == student_id)
    )
    assert count == 1
