from datetime import date

from pydantic import BaseModel, Field

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis


class StudentDetailsUpsertRequest(BaseModel):
    national_id: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    address: str | None = Field(default=None, max_length=300)
    home_language: str | None = Field(default=None, max_length=100)
    medical_diagnoses: list[Diagnosis] = Field(default_factory=list)
    emergency_contacts: list[ContactInfo] = Field(default_factory=list)
    legal_status: LegalStatus | None = None
    guardians: list[ContactInfo] = Field(default_factory=list)
