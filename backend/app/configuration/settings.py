from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.app.configuration.admin.bootstrap_admin_settings import BootstrapAdminSettings
from backend.app.configuration.app.app_settings import AppSettings
from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.configuration.database.database_settings import DatabaseSettings
from backend.app.configuration.email.email_settings import EmailSettings
from backend.app.configuration.maintenance.retention_settings import RetentionSettings
from backend.app.configuration.notifications.whatsapp_settings import WhatsAppSettings
from backend.app.configuration.pdf.brand_settings import BrandSettings

_PRODUCTION = "production"
_DEFAULT_DB_CREDENTIALS = "aleisiach:aleisiach@"
_PLACEHOLDER_ADMIN_PASSWORD = "change-me-123"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    whatsapp: WhatsAppSettings = Field(default_factory=WhatsAppSettings)
    brand: BrandSettings = Field(default_factory=BrandSettings)
    retention: RetentionSettings = Field(default_factory=RetentionSettings)
    bootstrap_admin: BootstrapAdminSettings = Field(default_factory=BootstrapAdminSettings)

    @model_validator(mode="after")
    def reject_development_defaults_in_production(self) -> Self:
        if self.app.environment != _PRODUCTION:
            return self
        problems = list(self._production_problems())
        if problems:
            joined = "; ".join(problems)
            raise ValueError(f"תצורת פרודקשן לא בטוחה: {joined}")
        return self

    def _production_problems(self) -> list[str]:
        problems: list[str] = []
        if self.email.provider == "console":
            problems.append("EMAIL_PROVIDER=console חושף קישורי הזמנה ואיפוס בלוגים")
        if self.email.provider == "smtp" and not self.email.smtp_starttls:
            problems.append("EMAIL_SMTP_STARTTLS=false שולח סיסמאות וטוקנים ללא הצפנה")
        if _DEFAULT_DB_CREDENTIALS in self.database.url:
            problems.append("DATABASE_URL עדיין מכיל את סיסמת ברירת המחדל")
        if self.app.trusted_proxy_count == 0:
            problems.append("APP_TRUSTED_PROXY_COUNT=0 מאחד את כל התעבורה לדלי rate-limit אחד")
        if any("localhost" in origin for origin in self.app.cors_origins):
            problems.append("APP_CORS_ORIGINS עדיין מפנה ל-localhost")
        if self.bootstrap_admin.password == _PLACEHOLDER_ADMIN_PASSWORD:
            problems.append("BOOTSTRAP_ADMIN_PASSWORD הוא סיסמת מציין מקום ידועה")
        return problems
