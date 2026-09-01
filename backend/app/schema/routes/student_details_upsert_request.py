from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from backend.app.models.client.legal_status import LegalStatus
from backend.app.schema.routes.contact_info import ContactInfo

OptionValue = Annotated[str, StringConstraints(min_length=1, max_length=200)]
FreeTextItem = Annotated[str, StringConstraints(min_length=1, max_length=500)]


class StudentDetailsUpsertRequest(BaseModel):
    national_id: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    address: str | None = Field(default=None, max_length=300)
    home_language: str | None = Field(default=None, max_length=100)
    idd_severity: str | None = Field(default=None, max_length=200)
    additional_diagnoses: list[OptionValue] = Field(default_factory=list)
    emergency_contacts: list[ContactInfo] = Field(default_factory=list)
    legal_status: LegalStatus | None = None
    guardians: list[ContactInfo] = Field(default_factory=list)
    has_allergies_or_dietary: bool = False
    allergies_dietary: list[FreeTextItem] = Field(default_factory=list)
    takes_regular_medication: bool = False
    medications: list[OptionValue] = Field(default_factory=list)
    medication_independence: str | None = Field(default=None, max_length=200)
    emergency_protocol: str | None = Field(default=None, max_length=5000)
    assistive_devices: list[OptionValue] = Field(default_factory=list)
    assistive_device_other: str | None = Field(default=None, max_length=200)
    expression_mode: str | None = Field(default=None, max_length=200)
    language_comprehension: str | None = Field(default=None, max_length=200)
    current_or_last_framework: str | None = Field(default=None, max_length=300)
    prior_task_experience: str | None = Field(default=None, max_length=2000)
    interests_strengths: str | None = Field(default=None, max_length=2000)
    triggers: str | None = Field(default=None, max_length=2000)
    distress_early_signs: str | None = Field(default=None, max_length=2000)
    calming_methods: str | None = Field(default=None, max_length=2000)
