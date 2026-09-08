from pydantic import BaseModel, Field

from backend.app.schema.routes.program_entry_request import ProgramEntryRequest


class ProgramUpsertRequest(BaseModel):
    entries: list[ProgramEntryRequest] = Field(default_factory=list)
