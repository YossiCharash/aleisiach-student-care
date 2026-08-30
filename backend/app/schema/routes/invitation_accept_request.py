from pydantic import BaseModel, Field

from backend.app.schema.routes.strong_password import StrongPassword


class InvitationAcceptRequest(BaseModel):
    token: str = Field(min_length=1)
    username: str = Field(min_length=3, max_length=80)
    password: StrongPassword
