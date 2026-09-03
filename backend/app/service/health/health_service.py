from backend.app.schema.routes.health_response import HealthResponse


class HealthService:
    def get_status(self) -> HealthResponse:
        return HealthResponse(status="ok")
