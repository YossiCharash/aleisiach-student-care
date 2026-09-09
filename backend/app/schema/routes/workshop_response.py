import uuid

from pydantic import BaseModel


class WorkshopResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: str
    instructor_id: uuid.UUID | None = None
    instructor_name: str | None = None
