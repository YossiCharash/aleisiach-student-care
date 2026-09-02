from collections.abc import Callable

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.configuration.admin.bootstrap_admin_settings import BootstrapAdminSettings
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.seed.bootstrap_admin_seeder import BootstrapAdminSeeder
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.password_policy import PasswordPolicy

_PASSWORD = "manager123"


def _settings(password: str = _PASSWORD, **overrides: str) -> BootstrapAdminSettings:
    values: dict[str, str] = {
        "email": "yossi@example.org",
        "username": "yossi",
        "full_name": "יוסי חרש",
        "password": password,
    }
    values.update(overrides)
    return BootstrapAdminSettings(_env_file=None, **values)


def _seeder(session: Session, settings: BootstrapAdminSettings) -> BootstrapAdminSeeder:
    return BootstrapAdminSeeder(session, PasswordHasher(), PasswordPolicy(8, 128), settings)


def _count_users(session: Session) -> int:
    with TenantBinding.platform(session):
        return session.scalar(select(func.count()).select_from(User)) or 0


def _only_user(session: Session) -> User:
    with TenantBinding.platform(session):
        return session.scalars(select(User)).one()


def test_creates_active_super_admin_when_configured(db_session: Session) -> None:
    created = _seeder(db_session, _settings()).run()

    assert created is True
    admin = _only_user(db_session)
    assert admin.role == UserRole.SUPER_ADMIN
    assert admin.status == UserStatus.ACTIVE
    assert admin.username == "yossi"
    assert admin.class_id is None
    assert admin.institution_id is None


def test_seeded_password_verifies(db_session: Session) -> None:
    _seeder(db_session, _settings()).run()

    admin = _only_user(db_session)
    assert admin.password_hash is not None
    assert PasswordHasher().verify(admin.password_hash, _PASSWORD)


def test_does_nothing_when_not_configured(db_session: Session) -> None:
    created = _seeder(db_session, _settings(password="")).run()

    assert created is False
    assert _count_users(db_session) == 0


def test_is_idempotent_when_a_super_admin_already_exists(
    db_session: Session, seed_user: Callable[..., User]
) -> None:
    seed_user("root", UserRole.SUPER_ADMIN)

    created = _seeder(db_session, _settings()).run()

    assert created is False
    assert _count_users(db_session) == 1


def test_seeds_even_when_an_institution_manager_exists(
    db_session: Session, seed_user: Callable[..., User]
) -> None:
    seed_user("mor", UserRole.MANAGER)

    created = _seeder(db_session, _settings()).run()

    assert created is True
    assert _count_users(db_session) == 2


def test_rejects_weak_password(db_session: Session) -> None:
    with pytest.raises(ValueError):
        _seeder(db_session, _settings(password="short1")).run()

    assert _count_users(db_session) == 0


def test_rejects_taken_email(db_session: Session, seed_user: Callable[..., User]) -> None:
    existing = seed_user("dana", UserRole.INSTRUCTOR)

    with pytest.raises(ValueError):
        _seeder(db_session, _settings(email=existing.email)).run()


def test_concurrent_insert_is_absorbed_instead_of_crashing(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = _settings()
    seeder = _seeder(db_session, settings)
    db_session.add(
        User(
            full_name="Racer",
            email=settings.email,
            username="racer",
            password_hash=PasswordHasher().hash(_PASSWORD),
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            institution_id=None,
        )
    )
    db_session.flush()
    monkeypatch.setattr(seeder, "_reject_taken_identity", lambda: None)
    monkeypatch.setattr(seeder, "_super_admin_exists", lambda: False)

    assert seeder.run() is False
