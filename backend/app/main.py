from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration.provider import get_settings
from app.errors.routes.error_handlers import register_error_handlers
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app.name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(health_router)
    return app


app = create_app()
