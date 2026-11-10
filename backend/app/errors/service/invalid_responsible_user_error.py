from backend.app.errors.service.app_error import AppError


class InvalidResponsibleUserError(AppError):
    status_code = 422
    code = "invalid_responsible_user"

    def __init__(self) -> None:
        super().__init__("אחד מאחראי הביצוע שנבחרו אינו משתמש במוסד.")
