import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.workshop_create_request import HEX_COLOR_PATTERN


class WorkshopUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str = Field(pattern=HEX_COLOR_PATTERN)
    instructor_id: uuid.UUID | None = None
