import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.base import Base


class StudentReportRepository[T: Base](ABC):
    _model: type[T]

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, student_id: uuid.UUID) -> T | None:
        return self._session.get(self._model, student_id)

    def create(self, report: T) -> tuple[T, bool]:
        try:
            with self._session.begin_nested():
                self._session.add(report)
                self._session.flush()
        except IntegrityError:
            existing = self.get(self._key(report))
            if existing is None:
                raise
            return existing, False
        return report, True

    def flush(self) -> None:
        self._session.flush()

    @abstractmethod
    def _key(self, report: T) -> uuid.UUID: ...
