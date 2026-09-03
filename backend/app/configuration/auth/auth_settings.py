from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AUTH_", env_file=".env", extra="ignore")

    session_ttl_minutes: int = 480
    invite_token_ttl_hours: int = 72
    reset_token_ttl_hours: int = 2
    max_failed_logins: int = 5
    lockout_minutes: int = 15
    reset_request_interval_minutes: int = 5
    rate_limit_max_attempts: int = 10
    rate_limit_window_seconds: int = 60
    password_min_length: int = 8
    password_max_length: int = 128
