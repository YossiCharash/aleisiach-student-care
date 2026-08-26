import uuid

from pydantic import BaseModel, ConfigDict

from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.meeting_entry_solution_response import (
    MeetingEntrySolutionResponse,
)


class MeetingEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: uuid.UUID
    skill_name_snapshot: str
    rating: MeetingRating
    solutions: list[MeetingEntrySolutionResponse]
