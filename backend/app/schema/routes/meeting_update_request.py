from pydantic import BaseModel, Field


class MeetingUpdateRequest(BaseModel):
    participants: str = Field(default="", max_length=2000)
    summary: str = Field(default="", max_length=10000)
