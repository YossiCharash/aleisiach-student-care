import uuid

from pydantic import BaseModel

from backend.app.schema.routes.incident_report_entry_response import IncidentReportEntryResponse


class IncidentReportHistoryResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    national_id: str | None = None
    entries: list[IncidentReportEntryResponse]
