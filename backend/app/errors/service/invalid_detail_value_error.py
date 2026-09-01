from backend.app.errors.service.app_error import AppError


class InvalidDetailValueError(AppError):
    status_code = 400
    code = "invalid_detail_value"

    def __init__(self, message: str) -> None:
        super().__init__(message)
