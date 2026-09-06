from backend.app.errors.service.app_error import AppError


class UserNotInvitedError(AppError):
    status_code = 409
    code = "user_not_invited"

    def __init__(self) -> None:
        super().__init__("אפשר לשלוח קישור התחברות מחדש רק למשתמש שההזמנה שלו עדיין ממתינה.")
