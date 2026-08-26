from backend.app.errors.service.authorization_error import AuthorizationError
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.schema.service.student_access_scope import StudentAccessScope

_ALL_CLASS_ROLES = frozenset({UserRole.MANAGER, UserRole.PROFESSIONAL_TEACHER})


class StudentAccessPolicy:
    @staticmethod
    def scope_for(user: User) -> StudentAccessScope:
        if user.role == UserRole.INSTRUCTOR:
            return StudentAccessScope(all_classes=False, class_id=user.class_id)
        if user.role in _ALL_CLASS_ROLES:
            return StudentAccessScope(all_classes=True)
        raise AuthorizationError

    @staticmethod
    def can_see_sensitive(user: User) -> bool:
        return user.role != UserRole.PROFESSIONAL_TEACHER
