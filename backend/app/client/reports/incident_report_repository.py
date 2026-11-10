import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.incident_report import IncidentReport


class IncidentReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, report: IncidentReport) -> IncidentReport:
        self._session.add(report)
        self._session.flush()
        return report

    def flush(self) -> None:
        self._session.flush()

    def get(self, report_id: uuid.UUID) -> IncidentReport | None:
        return self._session.get(IncidentReport, report_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[IncidentReport]:
        statement = (
            select(IncidentReport)
            .where(
                IncidentReport.student_id == student_id,
                IncidentReport.is_archived.is_(False),
            )
            .order_by(
                IncidentReport.event_date.desc(),
                IncidentReport.created_at.desc(),
                IncidentReport.id.desc(),
            )
        )
        return list(self._session.scalars(statement).all())
