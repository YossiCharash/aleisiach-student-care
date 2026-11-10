import uuid
from datetime import date

from pydantic import BaseModel

from backend.app.schema.routes.medical_summary_entry_response import MedicalSummaryEntryResponse


class MedicalSummaryHistoryResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    national_id: str | None = None
    date_of_birth: date | None = None
    address: str | None = None
    entries: list[MedicalSummaryEntryResponse]
