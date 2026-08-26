import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.client.social_note import SocialNote


class SocialNoteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, student_id: uuid.UUID) -> SocialNote | None:
        return self._session.get(SocialNote, student_id)

    def create(self, note: SocialNote) -> tuple[SocialNote, bool]:
        try:
            with self._session.begin_nested():
                self._session.add(note)
                self._session.flush()
        except IntegrityError:
            existing = self.get(note.student_id)
            if existing is None:
                raise
            return existing, False
        return note, True

    def flush(self) -> None:
        self._session.flush()
