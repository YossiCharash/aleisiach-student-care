import uuid
from datetime import date, datetime

from pydantic import BaseModel

from backend.app.schema.routes.risk_item_response import RiskItemResponse


class RiskAssessmentEntryResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    assessment_date: date
    items: list[RiskItemResponse]
    author_id: uuid.UUID
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime
