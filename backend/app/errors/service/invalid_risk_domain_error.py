from backend.app.errors.service.app_error import AppError


class InvalidRiskDomainError(AppError):
    status_code = 422
    code = "invalid_risk_domain"

    def __init__(self) -> None:
        super().__init__("אחד מתחומי הסיכון שנשלחו אינו פעיל במוסד.")
