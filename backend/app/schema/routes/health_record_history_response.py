import uuid

from pydantic import BaseModel

from backend.app.schema.routes.health_domain_response import HealthDomainResponse
from backend.app.schema.routes.health_record_response import HealthRecordResponse


class HealthRecordHistoryResponse(BaseModel):
    student_id: uuid.UUID
    student_name: str
    domains: list[HealthDomainResponse]
    entries: list[HealthRecordResponse]
