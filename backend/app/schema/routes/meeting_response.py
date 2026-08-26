import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.schema.routes.meeting_entry_response import MeetingEntryResponse


class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    year: int
    month: int
    author_id: uuid.UUID
    created_at: datetime
    entries: list[MeetingEntryResponse]
