import uuid

from pydantic import BaseModel, EmailStr

from backend.app.models.client.user_role import UserRole


class InvitationCommand(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    class_id: uuid.UUID | None = None
