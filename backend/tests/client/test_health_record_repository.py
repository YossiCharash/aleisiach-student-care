import uuid
from datetime import date

from sqlalchemy.orm import Session

from backend.app.client.reports.health_record_repository import HealthRecordRepository
from backend.app.models.client.health_record import HealthRecord
from backend.tests.support.seeding import seed_actor, seed_health_domains, seed_student


def _record(
    student_id: uuid.UUID, domain_id: uuid.UUID, author_id: uuid.UUID, record_date: date
) -> HealthRecord:
    return HealthRecord(
        student_id=student_id,
        domain_id=domain_id,
        record_date=record_date,
        support_given="x",
        author_id=author_id,
    )


def test_list_for_student_is_oldest_first_and_skips_archived(db_session: Session) -> None:
    student_id = seed_student(db_session)
    domain_id = seed_health_domains(db_session)[0].id
    author_id = seed_actor(db_session)
    repository = HealthRecordRepository(db_session)
    new = repository.add(_record(student_id, domain_id, author_id, date(2026, 6, 1)))
    old = repository.add(_record(student_id, domain_id, author_id, date(2026, 1, 1)))
    archived = repository.add(_record(student_id, domain_id, author_id, date(2026, 7, 1)))
    archived.is_archived = True
    repository.flush()

    listed = repository.list_for_student(student_id)

    assert [item.id for item in listed] == [old.id, new.id]
    assert repository.get(new.id) is new
