from backend.app.errors.service.app_error import AppError


class WorkshopNotEmptyError(AppError):
    status_code = 409
    code = "workshop_not_empty"

    def __init__(self, students: int, users: int) -> None:
        super().__init__(
            "לא ניתן להעביר את הסדנה לארכיון. "
            f"משויכים אליה כעת — חניכים פעילים: {students}, משתמשים: {users}."
        )
