from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="EMAIL_", env_file=".env", extra="ignore")

    provider: str = "console"
    from_address: str = "no-reply@aleisiach.local"
    invite_base_url: str = "http://localhost:5173/accept-invitation"
    reset_base_url: str = "http://localhost:5173/reset-password"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    smtp_timeout_seconds: float = 10.0
