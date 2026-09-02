from pydantic_settings import BaseSettings, SettingsConfigDict


class RetentionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RETENTION_", env_file=".env", extra="ignore")

    expired_credentials_days: int = 90
