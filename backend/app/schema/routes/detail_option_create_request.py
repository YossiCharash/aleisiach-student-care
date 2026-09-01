from pydantic import BaseModel, Field

from backend.app.models.client.detail_option_field import DetailOptionField


class DetailOptionCreateRequest(BaseModel):
    field: DetailOptionField
    name: str = Field(min_length=1, max_length=200)
