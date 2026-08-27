from backend.app.errors.service.app_error import AppError


class InvalidSectionTypeError(AppError):
    status_code = 400
    code = "invalid_section_type"

    def __init__(self, message: str) -> None:
        super().__init__(message)
