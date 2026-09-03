from pydantic import BaseModel

from backend.app.schema.routes.user_response import UserResponse


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
    institution_name: str | None = None
