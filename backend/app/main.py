from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuration.bootstrap import Bootstrap
from app.configuration.settings import Settings
from app.errors.routes.error_handlers import register_error_handlers
from app.routes.health import router as health_router


def create_app() -> FastAPI:
    bootstrap = Bootstrap(Settings())
    app = FastAPI(title=bootstrap.settings.app.name)
    app.state.bootstrap = bootstrap

    app.add_middleware(
        CORSMiddleware,
        allow_origins=bootstrap.settings.app.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(health_router)
    return app


app = create_app()
