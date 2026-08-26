import uuid
from datetime import date
from typing import Any

from sqlalchemy import JSON, Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.legal_status import LegalStatus


class StudentDetails(Base):
    __tablename__ = "student_details"

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), primary_key=True)
    national_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    home_language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    medical_diagnoses: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    emergency_contacts: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    legal_status: Mapped[LegalStatus | None] = mapped_column(
        Enum(LegalStatus, native_enum=False, length=32), nullable=True
    )
    guardians: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
