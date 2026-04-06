from pydantic import BaseModel, FutureDatetime
from typing import Optional


class createTask(BaseModel):
    user_id: int
    title: str
    status: Optional[int] = 1
    created_by: Optional[str] = None
    due_time: Optional[FutureDatetime] = None


class updateTask(BaseModel):
    title: Optional[str] = None
    status: Optional[int] = None
    due_time: Optional[FutureDatetime] = None
