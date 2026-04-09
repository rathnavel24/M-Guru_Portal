from pydantic import BaseModel

class PauseRequest(BaseModel):
    reason: str | None = None
