from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.settings import Settings
from backend.app.errors.routes.error_handlers import register_error_handlers
from backend.app.routes.auth import router as auth_router
from backend.app.routes.extra_section_types import router as extra_section_types_router
from backend.app.routes.health import router as health_router
from backend.app.routes.meetings import router as meetings_router
from backend.app.routes.program import router as program_router
from backend.app.routes.social_note import router as social_note_router
from backend.app.routes.student_details import router as student_details_router
from backend.app.routes.student_extra_sections import (
    router as student_extra_sections_router,
)
from backend.app.routes.students import router as students_router
from backend.app.routes.taxonomy import router as taxonomy_router
from backend.app.routes.users import router as users_router


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
    app.include_router(auth_router)
    app.include_router(students_router)
    app.include_router(taxonomy_router)
    app.include_router(meetings_router)
    app.include_router(program_router)
    app.include_router(student_details_router)
    app.include_router(social_note_router)
    app.include_router(users_router)
    app.include_router(extra_section_types_router)
    app.include_router(student_extra_sections_router)
    return app


app = create_app()
