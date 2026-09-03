import uuid

from pydantic import BaseModel


class TenantContext(BaseModel):
    institution_id: uuid.UUID
    institution_name: str
