import uuid

from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    label_id: uuid.UUID
    name: str
    order: int
    is_active: bool
    green_text: str
    yellow_text: str
    red_text: str
