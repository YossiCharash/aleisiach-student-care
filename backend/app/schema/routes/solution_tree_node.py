import uuid

from pydantic import BaseModel

from backend.app.models.client.meeting_rating import MeetingRating


class SolutionTreeNode(BaseModel):
    id: uuid.UUID
    text: str
    rating: MeetingRating
