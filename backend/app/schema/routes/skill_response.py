import uuid

from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sub_label_id: uuid.UUID
    name: str
    order: int
    is_active: bool
