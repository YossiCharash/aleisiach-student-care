from backend.app.errors.service.app_error import AppError


class CannotDisableSelfError(AppError):
    status_code = 400
    code = "cannot_disable_self"

    def __init__(self) -> None:
        super().__init__("You cannot disable your own account")
