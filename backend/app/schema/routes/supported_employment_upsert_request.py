from pydantic import BaseModel, Field

_MAX_FIELD = 5000


class SupportedEmploymentUpsertRequest(BaseModel):
    workplace: str = Field(default="", max_length=_MAX_FIELD)
    address: str = Field(default="", max_length=_MAX_FIELD)
    activity_type: str = Field(default="", max_length=_MAX_FIELD)
    work_process: str = Field(default="", max_length=_MAX_FIELD)
    work_environment: str = Field(default="", max_length=_MAX_FIELD)
    required_body_functions: str = Field(default="", max_length=_MAX_FIELD)
    hazards_and_safety: str = Field(default="", max_length=_MAX_FIELD)
    workplace_contact: str = Field(default="", max_length=_MAX_FIELD)
    escort_contact: str = Field(default="", max_length=_MAX_FIELD)
    mobility: str = Field(default="", max_length=_MAX_FIELD)
    work_hours: str = Field(default="", max_length=_MAX_FIELD)
