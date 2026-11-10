import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.medical_summary_entry import MedicalSummaryEntry


class MedicalSummaryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: MedicalSummaryEntry) -> MedicalSummaryEntry:
        self._session.add(entry)
        self._session.flush()
        return entry

    def flush(self) -> None:
        self._session.flush()

    def get(self, entry_id: uuid.UUID) -> MedicalSummaryEntry | None:
        return self._session.get(MedicalSummaryEntry, entry_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[MedicalSummaryEntry]:
        statement = (
            select(MedicalSummaryEntry)
            .where(
                MedicalSummaryEntry.student_id == student_id,
                MedicalSummaryEntry.is_archived.is_(False),
            )
            .order_by(
                MedicalSummaryEntry.summary_date.desc(),
                MedicalSummaryEntry.created_at.desc(),
                MedicalSummaryEntry.id.desc(),
            )
        )
        return list(self._session.scalars(statement).all())
