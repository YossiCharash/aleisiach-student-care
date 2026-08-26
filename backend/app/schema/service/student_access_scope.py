import uuid

from pydantic import BaseModel


class StudentAccessScope(BaseModel):
    all_classes: bool
    class_id: uuid.UUID | None = None

    def permits(self, class_id: uuid.UUID) -> bool:
        return self.all_classes or self.class_id == class_id
