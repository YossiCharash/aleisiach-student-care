from pydantic import BaseModel, Field

from backend.app.schema.routes.plan_entry_request import PlanEntryRequest


class PlanCreateRequest(BaseModel):
    entries: list[PlanEntryRequest] = Field(min_length=1)
