from backend.app.errors.service.app_error import AppError


class InvalidHealthDomainError(AppError):
    status_code = 422
    code = "invalid_health_domain"

    def __init__(self) -> None:
        super().__init__("התחום שנבחר אינו פעיל במוסד.")
