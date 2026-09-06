from typing import Annotated

from pydantic import BeforeValidator


def _strip(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    return value


NormalizedUsername = Annotated[str, BeforeValidator(_strip)]
