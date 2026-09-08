import uuid

from pydantic import BaseModel, ConfigDict

from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.program_entry_solution_response import (
    ProgramEntrySolutionResponse,
)


class ProgramEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: uuid.UUID
    skill_name_snapshot: str
    rating: MeetingRating
    solutions: list[ProgramEntrySolutionResponse]
