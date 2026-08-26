import uuid

from pydantic import BaseModel, Field


class SkillCreateRequest(BaseModel):
    sub_label_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
