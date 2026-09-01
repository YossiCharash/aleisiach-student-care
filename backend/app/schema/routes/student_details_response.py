import uuid
from datetime import date

from pydantic import BaseModel, Field

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo


class StudentDetailsResponse(BaseModel):
    student_id: uuid.UUID
    national_id: str | None = None
    date_of_birth: date | None = None
    age: int | None = None
    address: str | None = None
    home_language: str | None = None
    idd_severity: str | None = None
    additional_diagnoses: list[str] = Field(default_factory=list)
    emergency_contacts: list[ContactInfo] = Field(default_factory=list)
    legal_status: LegalStatus | None = None
    guardians: list[ContactInfo] = Field(default_factory=list)
    has_allergies_or_dietary: bool = False
    allergies_dietary: list[str] = Field(default_factory=list)
    takes_regular_medication: bool = False
    medications: list[str] = Field(default_factory=list)
    medication_independence: str | None = None
    emergency_protocol: str | None = None
    assistive_devices: list[str] = Field(default_factory=list)
    assistive_device_other: str | None = None
    expression_mode: str | None = None
    language_comprehension: str | None = None
    current_or_last_framework: str | None = None
    prior_task_experience: str | None = None
    interests_strengths: str | None = None
    triggers: str | None = None
    distress_early_signs: str | None = None
    calming_methods: str | None = None
    sensitive_visible: bool = True
