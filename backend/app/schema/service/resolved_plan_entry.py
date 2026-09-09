import uuid

from pydantic import BaseModel, Field

from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.service.resolved_solution import ResolvedSolution


class ResolvedPlanEntry(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    rating: MeetingRating
    solutions: list[ResolvedSolution] = Field(default_factory=list)
