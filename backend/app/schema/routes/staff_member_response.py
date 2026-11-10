import uuid

from pydantic import BaseModel


class StaffMemberResponse(BaseModel):
    id: uuid.UUID
    full_name: str
