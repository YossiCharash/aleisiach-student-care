import uuid
from datetime import date, time

from sqlalchemy.orm import Session

from backend.app.client.reports.incident_report_repository import IncidentReportRepository
from backend.app.models.client.incident_nature import IncidentNature
from backend.app.models.client.incident_report import IncidentReport
from backend.tests.support.seeding import seed_actor, seed_student


def _report(
    student_id: uuid.UUID,
    author_id: uuid.UUID,
    event_date: date = date(2026, 9, 1),
    description: str = "תיאור",
) -> IncidentReport:
    return IncidentReport(
        student_id=student_id,
        event_date=event_date,
        description=description,
        author_id=author_id,
    )


def test_add_then_get_roundtrip(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = IncidentReportRepository(db_session)
    report = _report(student_id, author_id)
    report.event_time = time(14, 30)
    report.natures = [IncidentNature.VIOLENCE, IncidentNature.OTHER]

    added = repository.add(report)

    fetched = repository.get(added.id)
    assert fetched is not None
    assert fetched.description == "תיאור"
    assert fetched.event_time == time(14, 30)
    assert fetched.natures == ["violence", "other"]
    assert fetched.referrals == []
    assert fetched.lessons_learned == ""


def test_list_excludes_archived_and_orders_newest_first(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session, "writer")
    repository = IncidentReportRepository(db_session)
    older = repository.add(_report(student_id, author_id, date(2026, 1, 1)))
    newer = repository.add(_report(student_id, author_id, date(2026, 9, 1)))
    hidden = repository.add(_report(student_id, author_id, date(2026, 12, 1)))
    hidden.is_archived = True
    repository.flush()

    listed = repository.list_for_student(student_id)

    assert [report.id for report in listed] == [newer.id, older.id]


def test_list_is_scoped_to_the_student(db_session: Session) -> None:
    student_id = seed_student(db_session)
    other_id = seed_student(db_session, "Other")
    author_id = seed_actor(db_session, "writer")
    repository = IncidentReportRepository(db_session)
    repository.add(_report(other_id, author_id))

    assert repository.list_for_student(student_id) == []
