import uuid

from pydantic import BaseModel

from backend.app.models.client.meeting_rating import MeetingRating


class ResolvedFocus(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    rating: MeetingRating
