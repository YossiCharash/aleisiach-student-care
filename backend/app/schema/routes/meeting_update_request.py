from pydantic import BaseModel, Field


class MeetingUpdateRequest(BaseModel):
    summary: str = Field(default="", max_length=10000)
