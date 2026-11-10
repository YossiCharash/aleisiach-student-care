import uuid
from datetime import date

from sqlalchemy.orm import Session

from backend.app.client.reports.risk_assessment_repository import RiskAssessmentRepository
from backend.app.models.client.risk_assessment import RiskAssessment
from backend.tests.support.seeding import seed_actor, seed_student


def _assessment(
    student_id: uuid.UUID, author_id: uuid.UUID, assessment_date: date = date(2026, 9, 1)
) -> RiskAssessment:
    return RiskAssessment(
        student_id=student_id,
        assessment_date=assessment_date,
        items=[{"domain": "weight", "nature": "x"}],
        author_id=author_id,
    )


def test_add_then_get_roundtrip(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session)
    repository = RiskAssessmentRepository(db_session)

    added = repository.add(_assessment(student_id, author_id))

    fetched = repository.get(added.id)
    assert fetched is not None
    assert fetched.items == [{"domain": "weight", "nature": "x"}]


def test_list_for_student_is_newest_first_and_skips_archived(db_session: Session) -> None:
    student_id = seed_student(db_session)
    author_id = seed_actor(db_session)
    repository = RiskAssessmentRepository(db_session)
    old = repository.add(_assessment(student_id, author_id, date(2026, 1, 1)))
    new = repository.add(_assessment(student_id, author_id, date(2026, 6, 1)))
    archived = repository.add(_assessment(student_id, author_id, date(2026, 7, 1)))
    archived.is_archived = True
    repository.flush()

    listed = repository.list_for_student(student_id)

    assert [item.id for item in listed] == [new.id, old.id]
