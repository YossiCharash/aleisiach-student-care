from backend.app.errors.service.app_error import AppError


class InvalidMeetingError(AppError):
    status_code = 422
    code = "invalid_meeting"

    def __init__(self, message: str) -> None:
        super().__init__(message)
