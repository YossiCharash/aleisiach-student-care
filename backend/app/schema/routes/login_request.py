from pydantic import BaseModel, Field

from backend.app.schema.routes.normalized_username import NormalizedUsername


class LoginRequest(BaseModel):
    username: NormalizedUsername = Field(min_length=1)
    password: str = Field(min_length=1)
