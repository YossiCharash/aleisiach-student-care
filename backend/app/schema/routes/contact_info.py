from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    relationship: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=40)
