from backend.app.errors.service.app_error import AppError


class CannotChangeOwnRoleError(AppError):
    status_code = 400
    code = "cannot_change_own_role"

    def __init__(self) -> None:
        super().__init__("אי אפשר לשנות את התפקיד של החשבון של עצמך.")
