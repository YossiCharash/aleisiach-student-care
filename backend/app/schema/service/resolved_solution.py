import uuid

from pydantic import BaseModel


class ResolvedSolution(BaseModel):
    solution_id: uuid.UUID
    solution_text: str
