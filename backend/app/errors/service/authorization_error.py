from backend.app.errors.service.app_error import AppError


class AuthorizationError(AppError):
    status_code = 403
    code = "forbidden"

    def __init__(self) -> None:
        super().__init__("You do not have permission to perform this action")
