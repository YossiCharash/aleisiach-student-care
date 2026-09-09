import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.skill_ratings_input import SkillRatingsInput


class SkillCreateRequest(BaseModel):
    sub_label_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    ratings: SkillRatingsInput
