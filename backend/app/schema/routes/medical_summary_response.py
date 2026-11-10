import uuid
from datetime import date, datetime

from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields


class MedicalSummaryResponse(MedicalSummaryFields):
    student_id: uuid.UUID
    exists: bool = False
    student_name: str
    national_id: str | None = None
    date_of_birth: date | None = None
    address: str | None = None
    written_by_name: str | None = None
    updated_at: datetime | None = None
