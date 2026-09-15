import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.reports.reception_report_repository import ReceptionReportRepository
from backend.app.models.client.reception_report import ReceptionReport
from backend.tests.support.seeding import seed_actor, seed_student


def _report(student_id: uuid.UUID, updated_by: uuid.UUID) -> ReceptionReport:
    return ReceptionReport(
        student_id=student_id,
        committee_summary="סיכום",
        updated_by=updated_by,
        updated_at=datetime.now(UTC),
    )


def test_create_inserts_when_absent(db_session: Session) -> None:
    student_id = seed_student(db_session)
    writer_id = seed_actor(db_session, "writer")
    repository = ReceptionReportRepository(db_session)

    report, created = repository.create(_report(student_id, writer_id))

    assert created is True
    assert report.student_id == student_id


def test_create_returns_existing_on_conflict(db_session: Session) -> None:
    student_id = seed_student(db_session)
    writer_id = seed_actor(db_session, "writer")
    repository = ReceptionReportRepository(db_session)
    repository.create(_report(student_id, writer_id))

    again, created = repository.create(_report(student_id, writer_id))

    assert created is False
    assert again.student_id == student_id
    count = db_session.scalar(
        select(func.count())
        .select_from(ReceptionReport)
        .where(ReceptionReport.student_id == student_id)
    )
    assert count == 1
