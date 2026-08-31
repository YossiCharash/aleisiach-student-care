from pydantic import BaseModel, Field

from backend.app.schema.routes.strong_password import StrongPassword


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: StrongPassword
