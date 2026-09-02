from pydantic import BaseModel


class PasswordChangeResponse(BaseModel):
    token: str
