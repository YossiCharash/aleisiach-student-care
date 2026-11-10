import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.workshop_instructor_response import WorkshopInstructorResponse


class WorkshopResponse(BaseModel):
    id: uuid.UUID
    name: str
    color: str
    instructors: list[WorkshopInstructorResponse] = Field(default_factory=list)
