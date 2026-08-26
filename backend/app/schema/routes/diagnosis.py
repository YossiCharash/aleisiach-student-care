from pydantic import BaseModel, Field


class Diagnosis(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    notes: str | None = Field(default=None, max_length=1000)
