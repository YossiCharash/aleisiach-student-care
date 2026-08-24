from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_", env_file=".env", extra="ignore")

    url: str = "postgresql+psycopg://aleisiach:aleisiach@localhost:5432/aleisiach"
    echo: bool = False
