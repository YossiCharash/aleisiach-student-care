from pydantic import BaseModel, Field

from backend.app.schema.routes.skill_rating_request import SkillRatingRequest


class MeetingCreateRequest(BaseModel):
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    entries: list[SkillRatingRequest] = Field(min_length=1)
