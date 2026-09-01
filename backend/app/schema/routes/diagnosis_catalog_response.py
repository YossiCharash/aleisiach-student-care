import uuid

from pydantic import BaseModel, ConfigDict


class DiagnosisCatalogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    order: int
    is_active: bool
