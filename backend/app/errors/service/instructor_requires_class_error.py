from backend.app.errors.service.app_error import AppError


class InstructorRequiresClassError(AppError):
    status_code = 400
    code = "instructor_requires_class"

    def __init__(self) -> None:
        super().__init__("יש לשייך כיתה למדריך.")
