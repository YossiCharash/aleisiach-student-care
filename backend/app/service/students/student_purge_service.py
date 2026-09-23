import uuid

from backend.app.client.students.student_purge_repository import StudentPurgeRepository
from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authentication_error import AuthenticationError
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.utils.service.password_hasher import PasswordHasher

_ENTITY_TYPE = "student"


class StudentPurgeService:
    def __init__(
        self,
        students: StudentRepository,
        purge_repository: StudentPurgeRepository,
        users: UserRepository,
        password_hasher: PasswordHasher,
        audit_logger: AuditLogger,
    ) -> None:
        self._students = students
        self._purge = purge_repository
        self._users = users
        self._password_hasher = password_hasher
        self._audit = audit_logger

    def delete(self, student_id: uuid.UUID, actor_id: uuid.UUID, password: str) -> None:
        self._verify_password(actor_id, password)
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

    def _verify_password(self, actor_id: uuid.UUID, password: str) -> None:
        actor = self._users.get_account(actor_id)
        if actor is None or actor.password_hash is None:
            raise AuthenticationError
        if not self._password_hasher.verify(actor.password_hash, password):
            raise InvalidCurrentPasswordError
