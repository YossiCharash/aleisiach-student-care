from datetime import date

from backend.app.schema.routes.medical_summary_request import MedicalSummaryRequest


class MedicalSummaryCreateRequest(MedicalSummaryRequest):
    summary_date: date
