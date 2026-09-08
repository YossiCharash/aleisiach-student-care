from pydantic import BaseModel, Field

from backend.app.schema.routes.skill_rating_request import SkillRatingRequest


class ProgramUpsertRequest(BaseModel):
    entries: list[SkillRatingRequest] = Field(min_length=1)
