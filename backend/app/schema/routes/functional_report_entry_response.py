import uuid
from datetime import date, datetime

from backend.app.schema.routes.functional_report_sections import FunctionalReportSections


class FunctionalReportEntryResponse(FunctionalReportSections):
    id: uuid.UUID
    student_id: uuid.UUID
    report_date: date
    author_id: uuid.UUID
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime
