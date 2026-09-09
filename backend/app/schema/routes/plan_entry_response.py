import uuid

from pydantic import BaseModel, ConfigDict

from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.schema.routes.plan_solution_response import PlanSolutionResponse


class PlanEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: uuid.UUID
    skill_name_snapshot: str
    rating: MeetingRating
    solutions: list[PlanSolutionResponse]
