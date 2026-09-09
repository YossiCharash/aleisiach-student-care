import uuid

from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.errors.service.cannot_change_own_role_error import CannotChangeOwnRoleError
from backend.app.errors.service.cannot_disable_self_error import CannotDisableSelfError
from backend.app.errors.service.email_already_used_error import EmailAlreadyUsedError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.errors.service.user_not_invited_error import UserNotInvitedError
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.schema.routes.user_response import UserResponse
from backend.app.schema.routes.user_update_request import UserUpdateRequest
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.audit.entity_audit_recorder import EntityAuditRecorder
from backend.app.service.auth.invitation_dispatcher import InvitationDispatcher

_PERMISSION_ENTITY_TYPE = "permission"
_USER_ENTITY_TYPE = "user"


class UserManagementService:
    def __init__(
        self,
        users: UserRepository,
        invitation_dispatcher: InvitationDispatcher,
        audit_logger: AuditLogger,
    ) -> None:
        self._users = users
        self._dispatcher = invitation_dispatcher
        self._users_audit = EntityAuditRecorder(audit_logger, _USER_ENTITY_TYPE)
        self._permissions_audit = EntityAuditRecorder(audit_logger, _PERMISSION_ENTITY_TYPE)

    def list_users(self) -> list[UserResponse]:
        return [UserResponse.model_validate(user) for user in self._users.list_all()]

    def update(
        self, user_id: uuid.UUID, request: UserUpdateRequest, actor_id: uuid.UUID
    ) -> UserResponse:
        if request.role is UserRole.SUPER_ADMIN:
            raise AuthorizationError
        user = self._require(user_id)
        if request.role is not user.role and user_id == actor_id:
            raise CannotChangeOwnRoleError
        self._require_email_available(request.email, user)
        changes = self._apply_update(user, request)
        if not changes:
            return UserResponse.model_validate(user)
        if "email" in changes and user.status is UserStatus.INVITED:
            self._dispatcher.dispatch(user.id, user.email)
        self._users_audit.record(actor_id, AuditAction.UPDATE, user.id, changes)
        return UserResponse.model_validate(user)

    def _require_email_available(self, email: str, user: User) -> None:
        if email == user.email:
            return
        if self._users.get_by_email(email) is not None:
            raise EmailAlreadyUsedError

    def _apply_update(self, user: User, request: UserUpdateRequest) -> list[str]:
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
            if request.role is not UserRole.INSTRUCTOR and user.workshop_id is not None:
                user.workshop_id = None
                changes.append("workshop_id")
        return changes

    def resend_invitation(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        user = self._require(user_id)
        if user.status is not UserStatus.INVITED:
            raise UserNotInvitedError
        self._dispatcher.dispatch(user.id, user.email)
        self._permissions_audit.record(actor_id, AuditAction.CREATE, user.id, ["invitation"])
        return UserResponse.model_validate(user)

    def disable(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        if user_id == actor_id:
            raise CannotDisableSelfError
        user = self._require(user_id)
        user.status = UserStatus.DISABLED
        self._dispatcher.revoke(user.id)
        self._permissions_audit.record(actor_id, AuditAction.ARCHIVE, user.id, ["status"])
        return UserResponse.model_validate(user)

    def enable(self, user_id: uuid.UUID, actor_id: uuid.UUID) -> UserResponse:
        user = self._require(user_id)
        user.status = UserStatus.ACTIVE if user.password_hash is not None else UserStatus.INVITED
        self._permissions_audit.record(actor_id, AuditAction.UPDATE, user.id, ["status"])
        return UserResponse.model_validate(user)

    def _require(self, user_id: uuid.UUID) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise NotFoundError("user")
        return user
