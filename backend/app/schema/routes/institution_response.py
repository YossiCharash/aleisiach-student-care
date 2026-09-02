import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstitutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    is_active: bool
    contact_name: str | None
    contact_phone: str | None
    created_at: datetime
