from pydantic import BaseModel, Field


class StudentExtraSectionUpsertRequest(BaseModel):
    content: str = Field(max_length=5000)
