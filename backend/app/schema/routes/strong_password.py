from typing import Annotated

from pydantic import AfterValidator

from backend.app.utils.service.password_policy import PasswordPolicy

_policy = PasswordPolicy()


def _enforce(value: str) -> str:
    error = _policy.validate(value)
    if error is not None:
        raise ValueError(error)
    return value


StrongPassword = Annotated[str, AfterValidator(_enforce)]
