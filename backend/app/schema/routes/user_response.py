import uuid

from pydantic import BaseModel, ConfigDict

from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    username: str | None
    role: UserRole
    status: UserStatus
