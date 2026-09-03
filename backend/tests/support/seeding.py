import uuid

from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.tests.conftest import DEFAULT_INSTITUTION_ID


def seed_actor(session: Session, username: str = "actor") -> uuid.UUID:
    user = User(
        full_name="Actor",
        email=f"{username}@example.com",
        username=username,
        role=UserRole.MANAGER,
        status=UserStatus.ACTIVE,
        institution_id=DEFAULT_INSTITUTION_ID,
    )
    session.add(user)
    session.flush()
    return user.id


def seed_student(session: Session, full_name: str = "Dana") -> uuid.UUID:
    class_entity = ClassEntity(name="Aleph")
    session.add(class_entity)
    session.flush()
    student = Student(full_name=full_name, class_id=class_entity.id)
    session.add(student)
    session.flush()
    return student.id
