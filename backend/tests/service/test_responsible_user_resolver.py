import uuid

import pytest
from sqlalchemy.orm import Session

from backend.app.client.students.student_repository import StudentRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_responsible_user_error import (
    InvalidResponsibleUserError,
)
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.service.users.responsible_user_resolver import ResponsibleUserResolver
from backend.tests.support.seeding import seed_actor, seed_student


def _setup(session: Session) -> tuple[ResponsibleUserResolver, Student, uuid.UUID]:
    student = StudentRepository(session).get(seed_student(session))
    assert student is not None
    return ResponsibleUserResolver(UserRepository(session)), student, seed_actor(session)


def _disable(session: Session, user_id: uuid.UUID) -> None:
    user = session.get(User, user_id)
    assert user is not None
    user.status = UserStatus.DISABLED
    session.flush()


def test_candidates_skip_disabled_users(db_session: Session) -> None:
    resolver, student, actor = _setup(db_session)
    disabled = seed_actor(db_session, "gone")
    _disable(db_session, disabled)

    ids = [member.id for member in resolver.candidates(student)]

    assert actor in ids
    assert disabled not in ids


def test_validate_rejects_unknown_and_newly_assigned_disabled_users(db_session: Session) -> None:
    resolver, student, actor = _setup(db_session)
    disabled = seed_actor(db_session, "gone")
    _disable(db_session, disabled)

    assert resolver.validate(student, [actor], set()) == {actor: "Actor"}
    assert disabled in resolver.validate(student, [disabled], {disabled})
    with pytest.raises(InvalidResponsibleUserError):
        resolver.validate(student, [disabled], set())
    with pytest.raises(InvalidResponsibleUserError):
        resolver.validate(student, [uuid.uuid4()], set())


def test_members_drop_unknown_ids_and_cache_names(db_session: Session) -> None:
    resolver, _, actor = _setup(db_session)
    cache: dict[uuid.UUID, str | None] = {}

    members = resolver.members([actor, uuid.uuid4()], cache)

    assert [member.id for member in members] == [actor]
    assert cache[actor] == "Actor"
