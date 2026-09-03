from backend.app.errors.service.app_error import AppError


class NoPendingManagerInvitationError(AppError):
    status_code = 409
    code = "no_pending_manager_invitation"

    def __init__(self) -> None:
        super().__init__("אין הזמנה ממתינה למנהל המוסד. אפשר לבקש איפוס סיסמה במסך הכניסה.")
