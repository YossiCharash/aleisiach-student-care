import uuid

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.cannot_disable_self_error import CannotDisableSelfError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger

_ENTITY_TYPE = "permission"


class UserManagementService:
    def __init__(self, users: UserRepository, audit_logger: AuditLogger) -> None:
        self._users = users
        self._audit = audit_logger

    def list_users(self) -> list[UserResponse]:
        return [UserResponse.model_validate(user) for user in self._users.list_all()]

    def disable(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        if user_id == actor_id:
            raise CannotDisableSelfError
        user = self._require(user_id)
        user.status = UserStatus.DISABLED
        self._record(actor_id, AuditAction.ARCHIVE, user.id)
        return UserResponse.model_validate(user)

    def enable(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        user = self._require(user_id)
        user.status = UserStatus.ACTIVE
        self._record(actor_id, AuditAction.UPDATE, user.id)
        return UserResponse.model_validate(user)

    def _require(self, user_id: uuid.UUID) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise NotFoundError("user")
        return user

    def _record(self, actor_id: uuid.UUID, action: AuditAction, entity_id: uuid.UUID) -> None:
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=action,
                entity_type=_ENTITY_TYPE,
                entity_id=entity_id,
                changes=["status"],
            )
        )
