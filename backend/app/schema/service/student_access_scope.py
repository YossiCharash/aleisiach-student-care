import uuid

from pydantic import BaseModel


class StudentAccessScope(BaseModel):
    all_classes: bool
    class_id: uuid.UUID | None = None
