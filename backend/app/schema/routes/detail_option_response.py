import uuid

from pydantic import BaseModel, ConfigDict

from backend.app.models.client.detail_option_field import DetailOptionField


class DetailOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    field: DetailOptionField
    name: str
    order: int
    is_active: bool
