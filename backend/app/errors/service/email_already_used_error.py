from app.errors.service.app_error import AppError


class EmailAlreadyUsedError(AppError):
    status_code = 409
    code = "email_already_used"

    def __init__(self) -> None:
        super().__init__("A user with this email already exists")
