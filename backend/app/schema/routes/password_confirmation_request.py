from pydantic import BaseModel, Field


class PasswordConfirmationRequest(BaseModel):
    password: str = Field(min_length=1)
