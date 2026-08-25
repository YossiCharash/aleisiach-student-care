from pydantic import BaseModel

from app.schema.routes.user_response import UserResponse


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
