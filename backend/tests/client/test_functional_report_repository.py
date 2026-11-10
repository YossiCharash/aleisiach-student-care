import uuid
from datetime import date

from sqlalchemy.orm import Session

from backend.app.client.reports.functional_report_repository import FunctionalReportRepository
from backend.app.models.client.functional_report_entry import FunctionalReportEntry
from backend.tests.support.seeding import seed_actor, seed_student


def _entry(
    student_id: uuid.UUID,
    author_id: uuid.UUID,
    report_date: date = date(2026, 9, 1),
    background: str = "רקע",
) -> FunctionalReportEntry:
    return FunctionalReportEntry(
        student_id=student_id,
        report_date=report_date,
        general_background=background,
        author_id=author_id,
    )


def test_add_then_get_roundtrip(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = FunctionalReportRepository(db_session)

    entry = repository.add(_entry(student_id, author_id))

    fetched = repository.get(entry.id)
    assert fetched is not None
    assert fetched.general_background == "רקע"
    assert fetched.summary_recommendations == ""


def test_list_excludes_archived_and_orders_newest_first(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = FunctionalReportRepository(db_session)
    older = repository.add(_entry(student_id, author_id, date(2026, 1, 1), "ישן"))
    newer = repository.add(_entry(student_id, author_id, date(2026, 9, 1), "חדש"))
    hidden = repository.add(_entry(student_id, author_id, date(2026, 12, 1), "מוסתר"))
    hidden.is_archived = True
    repository.flush()

    listed = repository.list_for_student(student_id)

    assert [entry.id for entry in listed] == [newer.id, older.id]


def test_list_is_per_student(db_session: Session) -> None:
    first = seed_student(db_session)
    second = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = FunctionalReportRepository(db_session)
    repository.add(_entry(first, author_id))

    assert repository.list_for_student(second) == []
