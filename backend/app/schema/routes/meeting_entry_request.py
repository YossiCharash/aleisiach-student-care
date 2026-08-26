import uuid

from pydantic import BaseModel, Field

from backend.app.models.client.meeting_rating import MeetingRating


class MeetingEntryRequest(BaseModel):
    skill_id: uuid.UUID
    rating: MeetingRating
    solution_ids: list[uuid.UUID] = Field(default_factory=list)
