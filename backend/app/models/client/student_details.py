import uuid
from datetime import date

from sqlalchemy import JSON, Boolean, Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.idd_severity import IddSeverity
from backend.app.models.client.legal_status import LegalStatus
from backend.app.models.client.medication_independence import MedicationIndependence


class StudentDetails(Base):
    __tablename__ = "student_details"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), primary_key=True)
    national_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    home_language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    idd_severity: Mapped[IddSeverity | None] = mapped_column(
        Enum(IddSeverity, native_enum=False, length=32), nullable=True
    )
    additional_diagnoses: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    emergency_contacts: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    legal_status: Mapped[LegalStatus | None] = mapped_column(
        Enum(LegalStatus, native_enum=False, length=32), nullable=True
    )
    guardians: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    has_allergies_or_dietary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allergies_dietary: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    takes_regular_medication: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    medications: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    medication_independence: Mapped[MedicationIndependence | None] = mapped_column(
        Enum(MedicationIndependence, native_enum=False, length=32), nullable=True
    )
    emergency_protocol: Mapped[str | None] = mapped_column(Text, nullable=True)
    assistive_devices: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    assistive_device_other: Mapped[str | None] = mapped_column(String(200), nullable=True)
