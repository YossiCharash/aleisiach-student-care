import uuid
from datetime import date, datetime

from backend.app.schema.routes.medical_summary_fields import MedicalSummaryFields


class MedicalSummaryEntryResponse(MedicalSummaryFields):
    id: uuid.UUID
    student_id: uuid.UUID
    summary_date: date
    author_id: uuid.UUID
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime
