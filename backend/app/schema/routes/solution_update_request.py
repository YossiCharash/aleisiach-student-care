from pydantic import BaseModel, Field


class SolutionUpdateRequest(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=500)
    is_active: bool | None = None
