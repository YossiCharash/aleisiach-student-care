from pydantic import BaseModel, Field


class ClassCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
