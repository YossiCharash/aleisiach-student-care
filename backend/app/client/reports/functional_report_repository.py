import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.functional_report_entry import FunctionalReportEntry


class FunctionalReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: FunctionalReportEntry) -> FunctionalReportEntry:
        self._session.add(entry)
        self._session.flush()
        return entry

    def flush(self) -> None:
        self._session.flush()

    def get(self, entry_id: uuid.UUID) -> FunctionalReportEntry | None:
        return self._session.get(FunctionalReportEntry, entry_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[FunctionalReportEntry]:
        statement = (
            select(FunctionalReportEntry)
            .where(
                FunctionalReportEntry.student_id == student_id,
                FunctionalReportEntry.is_archived.is_(False),
            )
            .order_by(
                FunctionalReportEntry.report_date.desc(),
                FunctionalReportEntry.created_at.desc(),
                FunctionalReportEntry.id.desc(),
            )
        )
        return list(self._session.scalars(statement).all())
