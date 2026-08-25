from app.errors.service.app_error import AppError


class AuthenticationError(AppError):
    status_code = 401
    code = "authentication_failed"

    def __init__(self) -> None:
        super().__init__("Invalid credentials")
