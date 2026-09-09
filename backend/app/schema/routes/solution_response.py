import uuid

from pydantic import BaseModel, ConfigDict

from backend.app.models.client.meeting_rating import MeetingRating


class SolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: uuid.UUID
    text: str
    rating: MeetingRating
    is_active: bool
