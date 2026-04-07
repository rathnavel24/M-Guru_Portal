from pydantic import BaseModel
from typing import Optional
from datetime import datetime 


class createTask(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    status: Optional[int] = 1
    created_by: Optional[int] = None
    due_time: Optional[datetime] = None

class updateTask(BaseModel):
    title: Optional[str] = None
    status: Optional[int] = None
    description: Optional[str] = None
    due_time: Optional[datetime] = None


class editTaskDetails(BaseModel):
    title: Optional[str] = None
    due_time: Optional[datetime] = None
