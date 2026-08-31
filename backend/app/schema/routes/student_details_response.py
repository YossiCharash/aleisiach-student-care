import uuid
from datetime import date

from pydantic import BaseModel, Field

from backend.app.models.client.assistive_device import AssistiveDevice
from backend.app.models.client.idd_severity import IddSeverity
from backend.app.models.client.legal_status import LegalStatus
from backend.app.models.client.medication_independence import MedicationIndependence
from backend.app.schema.routes.contact_info import ContactInfo


class StudentDetailsResponse(BaseModel):
    student_id: uuid.UUID
    national_id: str | None = None
    date_of_birth: date | None = None
    age: int | None = None
    address: str | None = None
    home_language: str | None = None
    idd_severity: IddSeverity | None = None
    additional_diagnoses: list[str] = Field(default_factory=list)
    emergency_contacts: list[ContactInfo] = Field(default_factory=list)
    legal_status: LegalStatus | None = None
    guardians: list[ContactInfo] = Field(default_factory=list)
    has_allergies_or_dietary: bool = False
    allergies_dietary: list[str] = Field(default_factory=list)
    takes_regular_medication: bool = False
    medications: list[str] = Field(default_factory=list)
    medication_independence: MedicationIndependence | None = None
    emergency_protocol: str | None = None
    assistive_devices: list[AssistiveDevice] = Field(default_factory=list)
    assistive_device_other: str | None = None
    sensitive_visible: bool = True
