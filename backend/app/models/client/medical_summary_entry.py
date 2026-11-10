import uuid
from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base
from backend.app.models.client.tenant_scoped import TenantScoped


class MedicalSummaryEntry(TenantScoped, Base):
    __tablename__ = "medical_summary_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id", "institution_id"],
            ["students.id", "students.institution_id"],
            name="fk_medical_summary_entries_student_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_medical_summary_entries_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    summary_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(Text, nullable=False, default="")
    lives_with: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    allergies: Mapped[str] = mapped_column(Text, nullable=False, default="")
    known_syndrome: Mapped[str] = mapped_column(Text, nullable=False, default="")
    background_diseases: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hospitalizations_surgeries: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dental_treatment: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    dentures: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    epilepsy_known: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    epilepsy_seizure_nature: Mapped[str] = mapped_column(Text, nullable=False, default="")
    epilepsy_seizure_frequency: Mapped[str] = mapped_column(Text, nullable=False, default="")
    epilepsy_last_seizure: Mapped[date | None] = mapped_column(Date, nullable=True)
    epilepsy_seizure_treatment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dual_diagnosis_known: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    dual_diagnosis_expression: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dual_diagnosis_frequency: Mapped[str] = mapped_column(Text, nullable=False, default="")
    dual_diagnosis_treatment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    skin_integrity: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    skin_known_issues: Mapped[str] = mapped_column(Text, nullable=False, default="")
    comprehension: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    communication: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    communication_other: Mapped[str] = mapped_column(Text, nullable=False, default="")
    speech: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    vision: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    hearing: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    functioning: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    mobility: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    eating: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    gastrostomy_feeding: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    formula: Mapped[str] = mapped_column(Text, nullable=False, default="")
    chewing_swallowing: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    food_texture: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    diet: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    diet_other: Mapped[str] = mapped_column(Text, nullable=False, default="")
    continence: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    loves: Mapped[str] = mapped_column(Text, nullable=False, default="")
    calming: Mapped[str] = mapped_column(Text, nullable=False, default="")
    angering: Mapped[str] = mapped_column(Text, nullable=False, default="")
    frightening: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stress_behavior: Mapped[str] = mapped_column(Text, nullable=False, default="")
    care_recommendations: Mapped[str] = mapped_column(Text, nullable=False, default="")
    general_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    guardian_name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    guardian_relation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    guardian_phone: Mapped[str] = mapped_column(Text, nullable=False, default="")
    health_fund: Mapped[str] = mapped_column(Text, nullable=False, default="")
    supplemental_insurance: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    supplemental_insurance_detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    attending_doctor: Mapped[str] = mapped_column(Text, nullable=False, default="")
    care_nurse: Mapped[str] = mapped_column(Text, nullable=False, default="")
    community_social_worker: Mapped[str] = mapped_column(Text, nullable=False, default="")
    social_worker_phone: Mapped[str] = mapped_column(Text, nullable=False, default="")
    filler_role: Mapped[str] = mapped_column(Text, nullable=False, default="")
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
