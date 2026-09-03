from pydantic_settings import BaseSettings, SettingsConfigDict


class BrandSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BRAND_", env_file=".env", extra="ignore")

    font_family: str = "'Heebo',sans-serif"
    primary_color: str = "#3F8420"
    accent_color: str = "#85C441"
    text_color: str = "#333333"
    muted_color: str = "#5C5C5C"
    surface_color: str = "#ffffff"
