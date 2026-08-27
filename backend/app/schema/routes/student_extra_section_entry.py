import uuid

from pydantic import BaseModel


class StudentExtraSectionEntry(BaseModel):
    section_type_id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None
    content: str | None
