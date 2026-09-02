from pydantic import BaseModel, Field


class InstitutionUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    contact_name: str | None = Field(default=None, max_length=200)
    contact_phone: str | None = Field(default=None, max_length=40)
