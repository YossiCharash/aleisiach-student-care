import uuid

from pydantic import BaseModel, Field


class PlanEntryRequest(BaseModel):
    skill_id: uuid.UUID
    solution_ids: list[uuid.UUID] = Field(min_length=1)
