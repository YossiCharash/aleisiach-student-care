import uuid

from pydantic import BaseModel, Field, field_validator

from backend.app.models.client.risk_level import RiskLevel

_MAX_NATURE = 2000
_MAX_PLAN = 5000
_MAX_RESPONSIBLE = 20


class RiskItemFields(BaseModel):
    domain_id: uuid.UUID
    nature: str = Field(default="", max_length=_MAX_NATURE)
    level: RiskLevel | None = None
    intervention_plan: str = Field(default="", max_length=_MAX_PLAN)
    responsible_user_ids: list[uuid.UUID] = Field(default_factory=list, max_length=_MAX_RESPONSIBLE)

    @field_validator("responsible_user_ids")
    @classmethod
    def _unique(cls, values: list[uuid.UUID]) -> list[uuid.UUID]:
        return list(dict.fromkeys(values))
