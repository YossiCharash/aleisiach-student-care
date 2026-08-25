from pydantic import BaseModel, Field


class InvitationAcceptRequest(BaseModel):
    token: str = Field(min_length=1)
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
