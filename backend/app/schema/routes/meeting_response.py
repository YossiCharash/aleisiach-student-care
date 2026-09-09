import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from backend.app.schema.routes.plan_entry_response import PlanEntryResponse
from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_strength import ProgramStrength


class MeetingResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    author_id: uuid.UUID
    meeting_date: date
    summary: str
    created_at: datetime
    updated_at: datetime
    strengths: list[ProgramStrength] = Field(default_factory=list)
    areas_to_strengthen: list[ProgramArea] = Field(default_factory=list)
    plan_entries: list[PlanEntryResponse] = Field(default_factory=list)
