import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.client.reception_report import ReceptionReport


class ReceptionReportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, student_id: uuid.UUID) -> ReceptionReport | None:
        return self._session.get(ReceptionReport, student_id)

    def create(self, report: ReceptionReport) -> tuple[ReceptionReport, bool]:
        try:
            with self._session.begin_nested():
                self._session.add(report)
                self._session.flush()
        except IntegrityError:
            existing = self.get(report.student_id)
            if existing is None:
                raise
            return existing, False
        return report, True

    def flush(self) -> None:
        self._session.flush()
