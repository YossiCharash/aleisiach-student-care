from typing import Annotated

from fastapi import Depends, Request

from backend.app.configuration.bootstrap import Bootstrap
from backend.app.configuration.settings import Settings


def get_bootstrap(request: Request) -> Bootstrap:
    bootstrap = request.app.state.bootstrap
    if not isinstance(bootstrap, Bootstrap):
        raise RuntimeError("Application bootstrap is not initialised")
    return bootstrap


def get_settings(bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)]) -> Settings:
    return bootstrap.settings
