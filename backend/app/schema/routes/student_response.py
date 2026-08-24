import uuid

from pydantic import BaseModel, ConfigDict


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    class_id: uuid.UUID
    full_name: str
    is_archived: bool
