import uuid

from pydantic import BaseModel

from backend.app.models.client.work_style import WorkStyle


class SupportedEmploymentResponse(BaseModel):
    student_id: uuid.UUID
    exists: bool = False
    workplace: str = ""
    work_style: WorkStyle | None = None
    address: str = ""
    activity_type: str = ""
    work_process: str = ""
    work_environment: str = ""
    required_body_functions: str = ""
    hazards_and_safety: str = ""
    workplace_contact: str = ""
    escort_contact: str = ""
    mobility: str = ""
    work_hours: str = ""
