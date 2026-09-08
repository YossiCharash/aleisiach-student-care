import uuid

from pydantic import BaseModel, Field

from backend.app.schema.routes.program_area import ProgramArea
from backend.app.schema.routes.program_entry_response import ProgramEntryResponse
from backend.app.schema.routes.program_strength import ProgramStrength


class ProgramResponse(BaseModel):
    student_id: uuid.UUID
    exists: bool = False
    entries: list[ProgramEntryResponse] = Field(default_factory=list)
    strengths: list[ProgramStrength] = Field(default_factory=list)
    areas_to_strengthen: list[ProgramArea] = Field(default_factory=list)
