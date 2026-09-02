from backend.app.schema.routes.institution_response import InstitutionResponse


class InstitutionSummary(InstitutionResponse):
    user_count: int
    student_count: int
    pending_manager_email: str | None = None
