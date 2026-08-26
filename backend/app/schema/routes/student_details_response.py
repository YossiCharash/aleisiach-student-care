import uuid
from datetime import date

from pydantic import BaseModel, Field

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis


class StudentDetailsResponse(BaseModel):
    student_id: uuid.UUID
    national_id: str | None = None
    date_of_birth: date | None = None
    age: int | None = None
    address: str | None = None
    home_language: str | None = None
    medical_diagnoses: list[Diagnosis] = Field(default_factory=list)
    emergency_contacts: list[ContactInfo] = Field(default_factory=list)
    legal_status: LegalStatus | None = None
    guardians: list[ContactInfo] = Field(default_factory=list)
    sensitive_visible: bool = True
