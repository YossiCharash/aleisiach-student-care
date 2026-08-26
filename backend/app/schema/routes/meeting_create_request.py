from pydantic import BaseModel, Field

from backend.app.schema.routes.meeting_entry_request import MeetingEntryRequest


class MeetingCreateRequest(BaseModel):
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    entries: list[MeetingEntryRequest] = Field(min_length=1)
