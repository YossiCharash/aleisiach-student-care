from pydantic import BaseModel, Field

_MAX_NOTE = 1000


class ReceptionChecklistItem(BaseModel):
    done: bool = False
    note: str = Field(default="", max_length=_MAX_NOTE)
