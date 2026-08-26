import uuid

from pydantic import BaseModel, ConfigDict


class SolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: uuid.UUID
    text: str
    is_active: bool
