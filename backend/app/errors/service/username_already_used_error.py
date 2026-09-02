from backend.app.errors.service.app_error import AppError


class UsernameAlreadyUsedError(AppError):
    status_code = 409
    code = "username_already_used"

    def __init__(self) -> None:
        super().__init__("שם המשתמש הזה כבר תפוס.")
