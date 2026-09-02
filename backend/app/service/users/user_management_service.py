import uuid

from backend.app.client.classes.class_repository import ClassRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.cannot_change_own_role_error import CannotChangeOwnRoleError
from backend.app.errors.service.cannot_disable_self_error import CannotDisableSelfError
from backend.app.errors.service.email_already_used_error import EmailAlreadyUsedError
from backend.app.errors.service.instructor_requires_class_error import (
    InstructorRequiresClassError,
)
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.routes.user_update_request import UserUpdateRequest
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher

_ENTITY_TYPE = "permission"


class UserManagementService:
    def __init__(
        self,
        users: UserRepository,
        classes: ClassRepository,
        invitation_dispatcher: InvitationDispatcher,
        audit_logger: AuditLogger,
    ) -> None:
        self._users = users
        self._classes = classes
        self._dispatcher = invitation_dispatcher
        self._audit = audit_logger

    def list_users(self) -> list[UserResponse]:
        return [UserResponse.model_validate(user) for user in self._users.list_all()]

    def update(
        self, user_id: uuid.UUID, request: UserUpdateRequest, actor_id: uuid.UUID
    ) -> UserResponse:
        user = self._require(user_id)
        class_id = request.class_id if request.role is UserRole.INSTRUCTOR else None
        if request.role is UserRole.INSTRUCTOR and class_id is None:
            raise InstructorRequiresClassError
        if class_id is not None and not self._classes.active_exists(class_id):
            raise NotFoundError("class")
        if request.role is not user.role and user_id == actor_id:
            raise CannotChangeOwnRoleError
        self._require_email_available(request.email, user)
        changes = self._apply_update(user, request, class_id)
        if not changes:
            return UserResponse.model_validate(user)
        if "email" in changes and user.status is UserStatus.INVITED:
            self._dispatcher.dispatch(user.id, user.email)
        self._audit.record(
            AuditEntry(
                actor_id=actor_id,
                action=AuditAction.UPDATE,
                entity_type=_ENTITY_TYPE,
                entity_id=user.id,
                changes=changes,
            )
        )
        return UserResponse.model_validate(user)

    def _require_email_available(self, email: str, user: User) -> None:
        if email == user.email:
            return
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyUsedError

    def _apply_update(
        self, user: User, request: UserUpdateRequest, class_id: uuid.UUID | None
    ) -> list[str]:
        changes: list[str] = []
        if user.full_name != request.full_name:
            user.full_name = request.full_name
            changes.append("full_name")
        if user.email != request.email:
            user.email = request.email
            changes.append("email")
        if user.role is not request.role:
            user.role = request.role
            changes.append("role")
        if user.class_id != class_id:
            user.class_id = class_id
            changes.append("class_id")
        return changes

    def disable(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        if user_id == actor_id:
            raise CannotDisableSelfError
        user = self._require(user_id)
        user.status = UserStatus.DISABLED
        self._record(actor_id, AuditAction.ARCHIVE, user.id)
        return UserResponse.model_validate(user)

    def enable(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        user = self._require(user_id)
        user.status = UserStatus.ACTIVE if user.password_hash is not None else UserStatus.INVITED
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
