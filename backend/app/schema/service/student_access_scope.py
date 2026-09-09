import uuid

from pydantic import BaseModel


class StudentAccessScope(BaseModel):
    all_workshops: bool
    workshop_id: uuid.UUID | None = None

    def permits(self, workshop_id: uuid.UUID) -> bool:
        return self.all_workshops or self.workshop_id == workshop_id
