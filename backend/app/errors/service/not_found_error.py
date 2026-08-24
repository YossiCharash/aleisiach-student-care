from app.errors.service.app_error import AppError


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"

    def __init__(self, resource: str) -> None:
        super().__init__(f"{resource} not found")
        self.resource = resource
