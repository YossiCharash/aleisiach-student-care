import uuid

from pydantic import BaseModel

from backend.app.schema.routes.risk_assessment_entry_response import RiskAssessmentEntryResponse
from backend.app.schema.routes.risk_domain_response import RiskDomainResponse


class RiskAssessmentHistoryResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    domains: list[RiskDomainResponse]
    entries: list[RiskAssessmentEntryResponse]
