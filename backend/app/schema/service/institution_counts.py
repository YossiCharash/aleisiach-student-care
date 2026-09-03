import uuid

from pydantic import BaseModel


class InstitutionCounts(BaseModel):
    institution_id: uuid.UUID
    user_count: int
    student_count: int
