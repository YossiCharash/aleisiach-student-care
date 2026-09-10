import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.social_note_entry import SocialNoteEntry


class SocialNoteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entry: SocialNoteEntry) -> SocialNoteEntry:
        self._session.add(entry)
        self._session.flush()
        return entry

    def flush(self) -> None:
        self._session.flush()

    def get(self, entry_id: uuid.UUID) -> SocialNoteEntry | None:
        return self._session.get(SocialNoteEntry, entry_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[SocialNoteEntry]:
        statement = (
            select(SocialNoteEntry)
            .where(
                SocialNoteEntry.student_id == student_id,
                SocialNoteEntry.is_archived.is_(False),
            )
            .order_by(
                SocialNoteEntry.note_date.desc(),
                SocialNoteEntry.created_at.desc(),
                SocialNoteEntry.id.desc(),
            )
        )
        return list(self._session.scalars(statement).all())
