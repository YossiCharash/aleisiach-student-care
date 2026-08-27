import uuid

from pydantic import BaseModel, Field


class ExtraSectionTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    parent_id: uuid.UUID | None = None
