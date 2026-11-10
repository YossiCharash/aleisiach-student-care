import uuid

from pydantic import BaseModel


class WorkshopInstructorResponse(BaseModel):
    id: uuid.UUID
    full_name: str
