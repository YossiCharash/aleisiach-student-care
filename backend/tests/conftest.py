import uuid
from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.client.database.provider import get_session
from backend.app.main import create_app
from backend.app.models.base import Base
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.utils.service.password_hasher import PasswordHasher


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def api(db_session: Session) -> Iterator[TestClient]:
    app = create_app()

    def override_session() -> Iterator[Session]:
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_user(db_session: Session) -> Callable[..., User]:
    def _seed(username: str, role: UserRole, class_id: uuid.UUID | None = None) -> User:
        user = User(
            full_name="User",
            email=f"{username}@example.com",
            username=username,
            password_hash=PasswordHasher().hash("password123"),
            role=role,
            class_id=class_id,
            status=UserStatus.ACTIVE,
        )
        db_session.add(user)
        db_session.flush()
        return user

    return _seed


@pytest.fixture
def auth_headers() -> Callable[..., dict[str, str]]:
    def _headers(api: TestClient, username: str, password: str = "password123") -> dict[str, str]:
        response = api.post("/auth/login", json={"username": username, "password": password})
        assert response.status_code == 200
        return {"Authorization": f"Bearer {response.json()['token']}"}

    return _headers
