from backend.app.errors.service.app_error import AppError


class RateLimitExceededError(AppError):
    status_code = 429
    code = "rate_limited"

    def __init__(self) -> None:
        super().__init__("יותר מדי בקשות. אנא המתינו רגע ונסו שוב.")
