import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.base import Base


class MeetingEntrySolution(Base):
    __tablename__ = "meeting_entry_solutions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    meeting_entry_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("meeting_entries.id"), nullable=False
    )
    solution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("solutions.id"), nullable=False)
    solution_text_snapshot: Mapped[str] = mapped_column(String(500), nullable=False)
