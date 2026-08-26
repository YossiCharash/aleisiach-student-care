import uuid

from pydantic import BaseModel, Field

from backend.app.models.client.meeting_rating import MeetingRating


class ProgramArea(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    rating: MeetingRating
    solutions: list[str] = Field(default_factory=list)
    year: int
    month: int
