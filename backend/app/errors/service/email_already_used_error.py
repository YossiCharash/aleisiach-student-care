from backend.app.errors.service.app_error import AppError


class EmailAlreadyUsedError(AppError):
    status_code = 409
    code = "email_already_used"

    def __init__(self) -> None:
        super().__init__("כתובת המייל הזו כבר רשומה במערכת.")
