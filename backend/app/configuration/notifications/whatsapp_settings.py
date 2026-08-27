from pydantic_settings import BaseSettings, SettingsConfigDict


class WhatsAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WHATSAPP_", env_file=".env", extra="ignore")

    provider: str = "console"
    enabled: bool = True
    webhook_url: str = ""
    webhook_timeout_seconds: float = 5.0
    recipient: str = ""
