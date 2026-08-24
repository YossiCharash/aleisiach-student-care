import uuid

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    class_id: uuid.UUID
