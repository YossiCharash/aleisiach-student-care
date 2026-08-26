from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.schema.service.student_access_scope import StudentAccessScope


class StudentAccessPolicy:
    @staticmethod
    def scope_for(user: User) -> StudentAccessScope:
        if user.role == UserRole.INSTRUCTOR:
            return StudentAccessScope(all_classes=False, class_id=user.class_id)
        return StudentAccessScope(all_classes=True)
