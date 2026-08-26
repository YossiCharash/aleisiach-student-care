import uuid

from pydantic import BaseModel


class ProgramStrength(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    year: int
    month: int
