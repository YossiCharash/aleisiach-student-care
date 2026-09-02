from backend.app.errors.service.app_error import AppError


class ClassNotEmptyError(AppError):
    status_code = 409
    code = "class_not_empty"

    def __init__(self, students: int, users: int) -> None:
        super().__init__(
            "לא ניתן להעביר את הכיתה לארכיון כל עוד משויכים אליה "
            f"{students} תלמידים פעילים ו-{users} משתמשים."
        )
