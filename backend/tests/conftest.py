import sqlite3
import uuid
from collections.abc import Callable, Iterator
from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.client.database.provider import get_session
from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.client.pdf.pdf_renderer import PdfRenderer
from backend.app.client.ratelimit.provider import get_rate_limiter
from backend.app.client.ratelimit.rate_limiter import RateLimiter
from backend.app.configuration.admin.bootstrap_admin_settings import BootstrapAdminSettings
from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.settings import Settings
from backend.app.main import create_app
from backend.app.models.base import Base
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.institution import Institution
from backend.app.models.client.student import Student
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.routes.pdf import get_pdf_renderer
from backend.app.utils.service.password_hasher import PasswordHasher

DEFAULT_INSTITUTION_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def _unseeded_app() -> FastAPI:
    settings = Settings()
    settings.bootstrap_admin = BootstrapAdminSettings(
        _env_file=None, email="", username="", full_name="", password=""
    )
    return create_app(Bootstrap(settings))


@pytest.fixture
def client() -> TestClient:
    return TestClient(_unseeded_app())


def _enforce_sqlite_foreign_keys(connection: object, _: object) -> None:
    if isinstance(connection, sqlite3.Connection):
        connection.execute("PRAGMA foreign_keys=ON")


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _enforce_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    session.add(
        Institution(id=DEFAULT_INSTITUTION_ID, name="מוסד בדיקה", code="test", is_active=True)
    )
    session.flush()
    TenantBinding.bind(session, DEFAULT_INSTITUTION_ID)
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def api(db_session: Session) -> Iterator[TestClient]:
    app = _unseeded_app()

    def override_session() -> Iterator[Session]:
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_pdf_renderer] = lambda: _StubPdfRenderer()
    app.dependency_overrides[get_rate_limiter] = lambda: _NoOpRateLimiter()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class _StubPdfRenderer(PdfRenderer):
    def render(self, html: str) -> bytes:
        return b"%PDF-1.4 stub"


class _NoOpRateLimiter(RateLimiter):
    def check(self, key: str, limit: int, window: timedelta) -> None:
        return None


@pytest.fixture
def seed_institution(db_session: Session) -> Callable[..., Institution]:
    def _seed(name: str, code: str, is_active: bool = True) -> Institution:
        institution = Institution(id=uuid.uuid4(), name=name, code=code, is_active=is_active)
        db_session.add(institution)
        db_session.flush()
        return institution

    return _seed


@pytest.fixture
def institution(db_session: Session) -> Institution:
    entity = db_session.get(Institution, DEFAULT_INSTITUTION_ID)
    assert entity is not None
    return entity


@pytest.fixture
def seed_user(db_session: Session, institution: Institution) -> Callable[..., User]:
    def _seed(
        username: str,
        role: UserRole,
        class_id: uuid.UUID | None = None,
        status: UserStatus = UserStatus.ACTIVE,
        institution_id: uuid.UUID | None = None,
    ) -> User:
        owner = None if role == UserRole.SUPER_ADMIN else (institution_id or institution.id)
        user = User(
            full_name="User",
            email=f"{username}@example.com",
            username=username,
            password_hash=PasswordHasher().hash("password123"),
            role=role,
            class_id=class_id,
            status=status,
            institution_id=owner,
        )
        db_session.add(user)
        db_session.flush()
        return user

    return _seed


@pytest.fixture
def seed_class(db_session: Session, institution: Institution) -> Callable[..., uuid.UUID]:
    def _seed(name: str = "Aleph", institution_id: uuid.UUID | None = None) -> uuid.UUID:
        entity = ClassEntity(name=name, institution_id=institution_id or institution.id)
        db_session.add(entity)
        db_session.flush()
        return entity.id

    return _seed


@pytest.fixture
def seed_student(db_session: Session, institution: Institution) -> Callable[..., uuid.UUID]:
    def _seed(
        class_id: uuid.UUID, full_name: str = "Dana", institution_id: uuid.UUID | None = None
    ) -> uuid.UUID:
        student = Student(
            full_name=full_name,
            class_id=class_id,
            institution_id=institution_id or institution.id,
        )
        db_session.add(student)
        db_session.flush()
        return student.id

    return _seed


@pytest.fixture
def auth_headers() -> Callable[..., dict[str, str]]:
    def _headers(api: TestClient, username: str, password: str = "password123") -> dict[str, str]:
        response = api.post("/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['token']}"}

    return _headers
