import uuid
from datetime import datetime

from backend.app.schema.routes.incident_report_fields import IncidentReportFields


class IncidentReportEntryResponse(IncidentReportFields):
    id: uuid.UUID
    student_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime
