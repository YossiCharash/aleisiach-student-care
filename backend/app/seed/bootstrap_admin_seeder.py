from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.configuration.admin.bootstrap_admin_settings import BootstrapAdminSettings
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole
from backend.app.models.client.user_status import UserStatus
from backend.app.utils.service.password_hasher import PasswordHasher
from backend.app.utils.service.password_policy import PasswordPolicy


class BootstrapAdminSeeder:
    def __init__(
        self,
        session: Session,
        password_hasher: PasswordHasher,
        password_policy: PasswordPolicy,
        settings: BootstrapAdminSettings,
    ) -> None:
        self._session = session
        self._hasher = password_hasher
        self._policy = password_policy
        self._settings = settings

    def run(self) -> bool:
        if not self._settings.is_configured:
            return False
        if self._manager_exists():
            return False
        self._reject_weak_password()
        self._reject_taken_identity()
        self._session.add(self._build_manager())
        try:
            self._session.flush()
        except IntegrityError:
            self._session.rollback()
            return False
        return True

    def _manager_exists(self) -> bool:
        statement = select(User.id).where(User.role == UserRole.MANAGER).limit(1)
        return self._session.scalar(statement) is not None

    def _reject_weak_password(self) -> None:
        error = self._policy.validate(self._settings.password)
        if error is not None:
            raise ValueError(f"סיסמת מנהל האתחול אינה תקינה: {error}")

    def _reject_taken_identity(self) -> None:
        if self._session.scalar(select(User).where(User.email == self._settings.email)) is not None:
            raise ValueError("כתובת המייל של מנהל האתחול כבר קיימת במערכת.")
        taken_username = select(User).where(User.username == self._settings.username)
        if self._session.scalar(taken_username) is not None:
            raise ValueError("שם המשתמש של מנהל האתחול כבר קיים במערכת.")

    def _build_manager(self) -> User:
        return User(
            full_name=self._settings.full_name,
            email=self._settings.email,
            username=self._settings.username,
            password_hash=self._hasher.hash(self._settings.password),
            role=UserRole.MANAGER,
            class_id=None,
            status=UserStatus.ACTIVE,
        )
