from pydantic_settings import BaseSettings, SettingsConfigDict


class BootstrapAdminSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOOTSTRAP_ADMIN_", env_file=".env", extra="ignore"
    )

    email: str = ""
    username: str = ""
    full_name: str = ""
    password: str = ""

    @property
    def is_configured(self) -> bool:
        return all(
            value.strip() for value in (self.email, self.username, self.full_name, self.password)
        )
