from pydantic import BaseModel


class CleanupResult(BaseModel):
    sessions_deleted: int
    tokens_deleted: int
    rate_limit_hits_deleted: int = 0
