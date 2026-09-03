from backend.app.errors.service.app_error import AppError


class InstitutionInactiveError(AppError):
    status_code = 403
    code = "institution_inactive"

    def __init__(self) -> None:
        super().__init__("המוסד שאליו החשבון משויך אינו פעיל. יש לפנות למנהל המערכת.")
