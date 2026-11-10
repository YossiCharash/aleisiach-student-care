import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.health_record import HealthRecord


class HealthRecordRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, record: HealthRecord) -> HealthRecord:
        self._session.add(record)
        self._session.flush()
        return record

    def flush(self) -> None:
        self._session.flush()

    def get(self, record_id: uuid.UUID) -> HealthRecord | None:
        return self._session.get(HealthRecord, record_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[HealthRecord]:
        statement = (
            select(HealthRecord)
            .where(
                HealthRecord.student_id == student_id,
                HealthRecord.is_archived.is_(False),
            )
            .order_by(
                HealthRecord.record_date.asc(),
                HealthRecord.created_at.asc(),
                HealthRecord.id.asc(),
            )
        )
        return list(self._session.scalars(statement).all())
