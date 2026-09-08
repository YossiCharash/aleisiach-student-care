import uuid

from sqlalchemy import Enum, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.program_entry_solution import ProgramEntrySolution
from backend.app.models.client.tenant_scoped import TenantScoped


class ProgramEntry(TenantScoped, Base):
    __tablename__ = "program_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["program_id", "institution_id"],
            ["programs.id", "programs.institution_id"],
            name="fk_program_entries_program_institution",
        ),
        ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_program_entries_skill_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_program_entries_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    skill_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    rating: Mapped[MeetingRating] = mapped_column(
        Enum(MeetingRating, native_enum=False, length=16), nullable=False
    )
    position: Mapped[int] = mapped_column("position", Integer, nullable=False)
    solutions: Mapped[list[ProgramEntrySolution]] = relationship(
        cascade="all, delete-orphan", order_by=ProgramEntrySolution.position
    )
