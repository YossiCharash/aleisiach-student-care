import uuid

from backend.app.client.reports.student_report_repository import StudentReportRepository
from backend.app.models.client.supported_employment import SupportedEmployment


class SupportedEmploymentRepository(StudentReportRepository[SupportedEmployment]):
    _model = SupportedEmployment

    def _key(self, report: SupportedEmployment) -> uuid.UUID:
        return report.student_id
