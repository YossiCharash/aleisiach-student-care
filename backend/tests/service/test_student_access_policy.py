import uuid

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.service.students.student_access_policy import StudentAccessPolicy


def _user(role: UserRole, class_id: uuid.UUID | None = None) -> User:
    return User(full_name="U", email="u@example.com", role=role, class_id=class_id)


def test_instructor_scope_limits_to_own_class() -> None:
    class_id = uuid.uuid4()

    scope = StudentAccessPolicy.scope_for(_user(UserRole.INSTRUCTOR, class_id))

    assert scope.all_classes is False
    assert scope.class_id == class_id


def test_manager_scope_sees_all_classes() -> None:
    scope = StudentAccessPolicy.scope_for(_user(UserRole.MANAGER))

    assert scope.all_classes is True


def test_professional_teacher_scope_sees_all_classes() -> None:
    scope = StudentAccessPolicy.scope_for(_user(UserRole.PROFESSIONAL_TEACHER))

    assert scope.all_classes is True
