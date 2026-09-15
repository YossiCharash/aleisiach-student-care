import uuid

from backend.app.client.reports.student_report_repository import StudentReportRepository
from backend.app.models.client.functional_report import FunctionalReport


class FunctionalReportRepository(StudentReportRepository[FunctionalReport]):
    _model = FunctionalReport

    def _key(self, report: FunctionalReport) -> uuid.UUID:
        return report.student_id
