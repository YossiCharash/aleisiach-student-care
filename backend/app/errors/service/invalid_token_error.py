from backend.app.errors.service.app_error import AppError


class InvalidTokenError(AppError):
    status_code = 400
    code = "invalid_token"

    def __init__(self) -> None:
        super().__init__("הקישור אינו תקין או שפג תוקפו.")
