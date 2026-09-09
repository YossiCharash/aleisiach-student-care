import uuid

from pydantic import BaseModel, Field

HEX_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"


class WorkshopCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str = Field(pattern=HEX_COLOR_PATTERN)
    instructor_id: uuid.UUID | None = None
