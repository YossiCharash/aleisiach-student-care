from datetime import date

from pydantic import BaseModel, Field


class MeetingCreateRequest(BaseModel):
    meeting_date: date
    participants: str = Field(default="", max_length=2000)
    summary: str = Field(default="", max_length=10000)
