import uuid

from sqlalchemy import Enum, ForeignKeyConstraint, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base
from backend.app.models.client.meeting_entry_solution import MeetingEntrySolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.tenant_scoped import TenantScoped


class MeetingEntry(TenantScoped, Base):
    __tablename__ = "meeting_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["meeting_id", "institution_id"],
            ["team_meetings.id", "team_meetings.institution_id"],
            name="fk_meeting_entries_meeting_institution",
        ),
        ForeignKeyConstraint(
            ["skill_id", "institution_id"],
            ["skills.id", "skills.institution_id"],
            name="fk_meeting_entries_skill_institution",
        ),
        UniqueConstraint("id", "institution_id", name="uq_meeting_entries_id_institution"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    skill_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    rating: Mapped[MeetingRating] = mapped_column(
        Enum(MeetingRating, native_enum=False, length=16), nullable=False
    )
    position: Mapped[int] = mapped_column("position", Integer, nullable=False)
    solutions: Mapped[list[MeetingEntrySolution]] = relationship(
        cascade="all, delete-orphan", order_by=MeetingEntrySolution.position
    )
