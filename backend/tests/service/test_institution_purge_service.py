import uuid
from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.institutions.institution_purge_repository import (
    InstitutionPurgeRepository,
)
from backend.app.client.institutions.institution_repository import InstitutionRepository
from backend.app.client.users.user_repository import UserRepository
from backend.app.errors.service.invalid_current_password_error import InvalidCurrentPasswordError
from backend.app.errors.service.not_found_error import NotFoundError
from backend.app.models.client.institution import Institution
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.service.institutions.institution_purge_service import InstitutionPurgeService
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.password_verifier import PasswordVerifier

SeedUser = Callable[..., User]
SeedInstitution = Callable[..., Institution]


def _service(session: Session) -> InstitutionPurgeService:
    return InstitutionPurgeService(
        InstitutionRepository(session),
        InstitutionPurgeRepository(session),
        PasswordVerifier(UserRepository(session), PasswordHasher()),
    )


def test_deletes_the_institution(
    db_session: Session, seed_institution: SeedInstitution, seed_user: SeedUser
) -> None:
    target_id = seed_institution("בית ספר ב").id
    admin_id = seed_user("root", UserRole.SUPER_ADMIN).id

    _service(db_session).delete(target_id, admin_id, "password123")

    with TenantBinding.platform(db_session):
        assert db_session.get(Institution, target_id) is None


def test_wrong_password_raises_and_keeps_the_institution(
    db_session: Session, seed_institution: SeedInstitution, seed_user: SeedUser
) -> None:
    target_id = seed_institution("בית ספר ב").id
    admin_id = seed_user("root", UserRole.SUPER_ADMIN).id

    with pytest.raises(InvalidCurrentPasswordError):
        _service(db_session).delete(target_id, admin_id, "nope")

    with TenantBinding.platform(db_session):
        assert db_session.get(Institution, target_id) is not None


def test_unknown_institution_raises_not_found(db_session: Session, seed_user: SeedUser) -> None:
    admin_id = seed_user("root", UserRole.SUPER_ADMIN).id

    with pytest.raises(NotFoundError):
        _service(db_session).delete(uuid.uuid4(), admin_id, "password123")
