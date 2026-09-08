import uuid

from pydantic import BaseModel, ConfigDict


class ProgramEntrySolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    solution_id: uuid.UUID
    solution_text_snapshot: str
