import uuid
from datetime import date

from pydantic import BaseModel

from backend.app.schema.routes.functional_report_entry_response import (
    FunctionalReportEntryResponse,
)


class FunctionalReportHistoryResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    national_id: str | None = None
    date_of_birth: date | None = None
    entries: list[FunctionalReportEntryResponse]
