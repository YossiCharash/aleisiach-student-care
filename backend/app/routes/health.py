from typing import Annotated

from fastapi import APIRouter, Depends

from app.configuration.provider import get_settings
from app.configuration.settings import Settings
from app.schema.routes.health_response import HealthResponse
from app.service.health.health_service import HealthService


def get_health_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthService:
    return HealthService(app_settings=settings.app)


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def read_health(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    return service.get_status()
