import uuid

from pydantic import BaseModel

from backend.app.models.client.meeting_rating import MeetingRating


class FocusRatingRequest(BaseModel):
    skill_id: uuid.UUID
    rating: MeetingRating
