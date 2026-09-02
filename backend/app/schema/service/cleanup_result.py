from pydantic import BaseModel


class CleanupResult(BaseModel):
    sessions_deleted: int
    tokens_deleted: int
