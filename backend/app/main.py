from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.settings import Settings
from backend.app.errors.routes.error_handlers import register_error_handlers
from backend.app.routes.auth import router as auth_router
from backend.app.routes.classes import router as classes_router
from backend.app.routes.detail_options import router as detail_options_router
from backend.app.routes.diagnoses import router as diagnoses_router
from backend.app.routes.extra_section_types import router as extra_section_types_router
from backend.app.routes.health import router as health_router
from backend.app.routes.institutions import router as institutions_router
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
from backend.app.seed.bootstrap_admin_seeder import BootstrapAdminSeeder
from backend.app.utils.routes.security_headers_middleware import SecurityHeadersMiddleware
from backend.app.utils.service.password_policy import PasswordPolicy


def seed_bootstrap_admin(bootstrap: Bootstrap) -> None:
    if not bootstrap.settings.bootstrap_admin.is_configured:
        return
    policy = PasswordPolicy(
        bootstrap.settings.auth.password_min_length,
        bootstrap.settings.auth.password_max_length,
    )
    generator = bootstrap.database.session()
    session = next(generator)
    try:
        BootstrapAdminSeeder(
            session, bootstrap.password_hasher, policy, bootstrap.settings.bootstrap_admin
        ).run()
    except BaseException:
        session.rollback()
        raise
    finally:
        next(generator, None)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    seed_bootstrap_admin(app.state.bootstrap)
    yield


def create_app(bootstrap: Bootstrap | None = None) -> FastAPI:
    bootstrap = bootstrap or Bootstrap(Settings())
    is_production = bootstrap.settings.app.environment == "production"
    app = FastAPI(
        title=bootstrap.settings.app.name,
        docs_url=None if is_production else "/docs",
        redoc_url=None if is_production else "/redoc",
        openapi_url=None if is_production else "/openapi.json",
        lifespan=lifespan,
    )
    app.state.bootstrap = bootstrap
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_max_age_seconds=(
            bootstrap.settings.app.hsts_max_age_seconds if is_production else None
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=bootstrap.settings.app.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(institutions_router)
    app.include_router(students_router)
    app.include_router(classes_router)
    app.include_router(diagnoses_router)
    app.include_router(detail_options_router)
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
