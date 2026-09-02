from backend.app.errors.service.app_error import AppError


class InstitutionCodeTakenError(AppError):
    status_code = 409
    code = "institution_code_taken"

    def __init__(self) -> None:
        super().__init__("קוד המוסד כבר קיים במערכת. יש לבחור קוד אחר.")
