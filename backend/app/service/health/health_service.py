from backend.app.configuration.app.app_settings import AppSettings
from backend.app.schema.routes.health_response import HealthResponse


class HealthService:
    def __init__(self, app_settings: AppSettings) -> None:
        self._app_settings = app_settings

    def get_status(self) -> HealthResponse:
        return HealthResponse(status="ok", environment=self._app_settings.environment)
