import uuid

from backend.app.client.reports.student_report_repository import StudentReportRepository
from backend.app.models.client.medical_summary import MedicalSummary


class MedicalSummaryRepository(StudentReportRepository[MedicalSummary]):
    _model = MedicalSummary

    def _key(self, report: MedicalSummary) -> uuid.UUID:
        return report.student_id
