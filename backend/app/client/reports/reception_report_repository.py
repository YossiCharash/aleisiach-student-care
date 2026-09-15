import uuid

from backend.app.client.reports.student_report_repository import StudentReportRepository
from backend.app.models.client.reception_report import ReceptionReport


class ReceptionReportRepository(StudentReportRepository[ReceptionReport]):
    _model = ReceptionReport

    def _key(self, report: ReceptionReport) -> uuid.UUID:
        return report.student_id
