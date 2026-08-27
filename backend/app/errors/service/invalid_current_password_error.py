from backend.app.errors.service.app_error import AppError


class InvalidCurrentPasswordError(AppError):
    status_code = 400
    code = "invalid_current_password"

    def __init__(self) -> None:
        super().__init__("הסיסמה הנוכחית שגויה.")
