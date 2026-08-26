import uuid

from pydantic import BaseModel, Field


class SolutionCreateRequest(BaseModel):
    skill_id: uuid.UUID
    text: str = Field(min_length=1, max_length=500)
