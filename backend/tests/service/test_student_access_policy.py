import uuid

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.service.students.student_access_policy import StudentAccessPolicy


def _user(role: UserRole, workshop_id: uuid.UUID | None = None) -> User:
    return User(full_name="U", email="u@example.com", role=role, workshop_id=workshop_id)


def test_instructor_scope_limits_to_own_workshop() -> None:
    workshop_id = uuid.uuid4()

    scope = StudentAccessPolicy.scope_for(_user(UserRole.INSTRUCTOR, workshop_id))

    assert scope.all_workshops is False
    assert scope.workshop_id == workshop_id


def test_manager_scope_sees_all_workshops() -> None:
    scope = StudentAccessPolicy.scope_for(_user(UserRole.MANAGER))

    assert scope.all_workshops is True


def test_professional_teacher_scope_sees_all_workshops() -> None:
    scope = StudentAccessPolicy.scope_for(_user(UserRole.PROFESSIONAL_TEACHER))

    assert scope.all_workshops is True
