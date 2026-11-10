import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.reports.medical_summary_repository import MedicalSummaryRepository
from backend.app.models.client.medical_summary import MedicalSummary
from backend.tests.support.seeding import seed_actor, seed_student


def _summary(student_id: uuid.UUID, updated_by: uuid.UUID) -> MedicalSummary:
    return MedicalSummary(
        student_id=student_id,
        allergies="בוטנים",
        mobility=["escort"],
        updated_by=updated_by,
        updated_at=datetime.now(UTC),
    )


def test_create_inserts_when_absent(db_session: Session) -> None:
    student_id = seed_student(db_session)
    writer_id = seed_actor(db_session, "writer")
    repository = MedicalSummaryRepository(db_session)

    summary, created = repository.create(_summary(student_id, writer_id))

    assert created is True
    assert repository.get(student_id) is summary
    assert summary.mobility == ["escort"]


def test_create_returns_existing_on_conflict(db_session: Session) -> None:
    student_id = seed_student(db_session)
    writer_id = seed_actor(db_session, "writer")
    repository = MedicalSummaryRepository(db_session)
    repository.create(_summary(student_id, writer_id))

    again, created = repository.create(_summary(student_id, writer_id))

    assert created is False
    count = db_session.scalar(
        select(func.count())
        .select_from(MedicalSummary)
        .where(MedicalSummary.student_id == student_id)
    )
    assert count == 1
    assert again.student_id == student_id
