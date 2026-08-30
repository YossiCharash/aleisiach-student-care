from typing import Annotated

from pydantic import AfterValidator

from backend.app.configuration.auth.auth_settings import AuthSettings
from backend.app.utils.service.password_policy import PasswordPolicy

_settings = AuthSettings()
_policy = PasswordPolicy(_settings.password_min_length, _settings.password_max_length)


def _enforce(value: str) -> str:
    error = _policy.validate(value)
    if error is not None:
        raise ValueError(error)
    return value


StrongPassword = Annotated[str, AfterValidator(_enforce)]
