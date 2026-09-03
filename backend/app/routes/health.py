from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.schema.routes.health_response import HealthResponse
from backend.app.service.health.health_service import HealthService


def get_health_service() -> HealthService:
    return HealthService()


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def read_health(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    return service.get_status()
