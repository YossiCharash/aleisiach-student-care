from pydantic import BaseModel, EmailStr, Field


class InstitutionCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    code: str = Field(min_length=2, max_length=40, pattern=r"^[a-z0-9-]+$")
    manager_full_name: str = Field(min_length=2, max_length=200)
    manager_email: EmailStr
    contact_name: str | None = Field(default=None, max_length=200)
    contact_phone: str | None = Field(default=None, max_length=40)
