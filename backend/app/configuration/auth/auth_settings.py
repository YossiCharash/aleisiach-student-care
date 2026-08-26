from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")

    password_hash_scheme: str = "argon2"
    session_ttl_minutes: int = 480
    invite_token_ttl_hours: int = 72
    reset_token_ttl_hours: int = 2
    max_failed_logins: int = 5
    lockout_minutes: int = 15
    reset_request_interval_minutes: int = 5
