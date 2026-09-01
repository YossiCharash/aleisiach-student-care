from pydantic import BaseModel, Field


class DetailOptionUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
