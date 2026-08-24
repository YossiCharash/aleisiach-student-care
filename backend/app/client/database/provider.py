from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.configuration.bootstrap import Bootstrap
from app.configuration.provider import get_bootstrap


def get_session(
    bootstrap: Annotated[Bootstrap, Depends(get_bootstrap)],
) -> Iterator[Session]:
    yield from bootstrap.database.session()
