import uuid
from datetime import date

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    class_id: uuid.UUID
    national_id: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
