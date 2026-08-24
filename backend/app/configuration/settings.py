from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.configuration.app.app_settings import AppSettings
from app.configuration.auth.auth_settings import AuthSettings
from app.configuration.database.database_settings import DatabaseSettings
from app.configuration.email.email_settings import EmailSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
