import uuid
from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator

from backend.app.models.client.risk_category import RiskCategory
from backend.app.models.client.risk_labels import RISK_CATEGORY_LABELS


class RiskDomainResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: RiskCategory
    name: str
    order: int
    is_active: bool
    category_label: str = ""

    @model_validator(mode="after")
    def _label_category(self) -> Self:
        self.category_label = RISK_CATEGORY_LABELS[self.category]
        return self
