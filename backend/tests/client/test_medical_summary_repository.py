import uuid
from datetime import date

from sqlalchemy.orm import Session

from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.models.client.medical_summary_entry import MedicalSummaryEntry
from backend.tests.support.seeding import seed_actor, seed_student


def _entry(student_id: uuid.UUID, author_id: uuid.UUID, summary_date: date) -> MedicalSummaryEntry:
    return MedicalSummaryEntry(
        student_id=student_id,
        summary_date=summary_date,
        allergies="בוטנים",
        mobility=["escort"],
        author_id=author_id,
    )


def test_add_then_get(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = MedicalSummaryRepository(db_session)

    entry = repository.add(_entry(student_id, author_id, date(2026, 11, 1)))

    assert repository.get(entry.id) is entry
    assert entry.mobility == ["escort"]


def test_list_is_newest_first_and_skips_archived(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = MedicalSummaryRepository(db_session)
    older = repository.add(_entry(student_id, author_id, date(2026, 1, 1)))
    newer = repository.add(_entry(student_id, author_id, date(2026, 6, 1)))
    archived = repository.add(_entry(student_id, author_id, date(2026, 9, 1)))
    archived.is_archived = True
    repository.flush()

    listed = repository.list_for_student(student_id)

    assert [entry.id for entry in listed] == [newer.id, older.id]


def test_list_is_scoped_to_the_student(db_session: Session) -> None:
    student_id = seed_student(db_session)
    other_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = MedicalSummaryRepository(db_session)
    repository.add(_entry(other_id, author_id, date(2026, 1, 1)))

    assert repository.list_for_student(student_id) == []
