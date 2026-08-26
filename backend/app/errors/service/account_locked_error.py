from backend.app.errors.service.app_error import AppError


class AccountLockedError(AppError):
    status_code = 429
    code = "account_locked"

    def __init__(self) -> None:
        super().__init__("Too many failed attempts; try again later")
