from pydantic import Field

from backend.app.schema.routes.risk_item_fields import RiskItemFields
from backend.app.schema.routes.staff_member_response import StaffMemberResponse


class RiskItemResponse(RiskItemFields):
    responsible: list[StaffMemberResponse] = Field(default_factory=list)
