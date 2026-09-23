import uuid

from backend.app.client.students.student_purge_repository import StudentPurgeRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.utils.service.password_verifier import PasswordVerifier

_ENTITY_TYPE = "student"


class StudentPurgeService:
    def __init__(
        self,
        students: StudentRepository,
        purge_repository: StudentPurgeRepository,
        password_verifier: PasswordVerifier,
        audit_logger: AuditLogger,
    ) -> None:
        self._students = students
        self._purge = purge_repository
        self._password_verifier = password_verifier
        self._audit = audit_logger

    def delete(self, student_id: uuid.UUID, actor_id: uuid.UUID, password: str) -> None:
        self._password_verifier.verify(actor_id, password)
        student = self._students.get(student_id)
        if student is None:
            raise NotFoundError(_ENTITY_TYPE)
        self._purge.purge(student_id)
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.DELETE,
                entity_type=_ENTITY_TYPE,
                entity_id=student_id,
            )
        )
