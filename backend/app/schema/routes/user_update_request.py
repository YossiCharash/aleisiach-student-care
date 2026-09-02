import uuid

from pydantic import BaseModel, EmailStr, Field

from backend.app.models.client.user_role import UserRole


class UserUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    role: UserRole
    class_id: uuid.UUID | None = None
