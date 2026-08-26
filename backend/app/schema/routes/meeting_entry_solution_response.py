import uuid

from pydantic import BaseModel, ConfigDict


class MeetingEntrySolutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    solution_id: uuid.UUID
    solution_text_snapshot: str
