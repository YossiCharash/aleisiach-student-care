from pydantic import BaseModel


class AuthEventContext(BaseModel):
    ip: str | None = None
    user_agent: str | None = None
