from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_", env_file=".env", extra="ignore")

    provider: str = "console"
    from_address: str = "no-reply@aleisiach.local"
    invite_base_url: str = "http://localhost:5173/invite"
    reset_base_url: str = "http://localhost:5173/reset-password"
