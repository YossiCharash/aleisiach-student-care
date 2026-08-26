import uuid

from pydantic import BaseModel, Field


class SubLabelCreateRequest(BaseModel):
    label_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
