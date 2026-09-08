from backend.app.errors.service.app_error import AppError


class InvalidSkillRatingError(AppError):
    status_code = 422
    code = "invalid_skill_rating"

    def __init__(self, message: str) -> None:
        super().__init__(message)
