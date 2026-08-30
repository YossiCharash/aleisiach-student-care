from pydantic import BaseModel, Field

from backend.app.schema.routes.strong_password import StrongPassword


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: StrongPassword
