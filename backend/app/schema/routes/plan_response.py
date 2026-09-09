import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.schema.routes.plan_entry_response import PlanEntryResponse


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    entries: list[PlanEntryResponse]
