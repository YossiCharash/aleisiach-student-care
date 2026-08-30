from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    name: str = "Aleisiach Student Care"
    environment: str = "local"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:8080"]
    hsts_max_age_seconds: int = 31536000
    trusted_proxy_count: int = 0

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
