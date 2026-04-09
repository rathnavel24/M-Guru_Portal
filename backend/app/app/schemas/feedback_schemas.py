from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Create
class FeedbackCreate(BaseModel):
    assigned_to: Optional[int] = None  # admin/mentor user_id   
    category: str
    message: str


# Reply
class FeedbackReply(BaseModel):
    feedback_id: int
    reply: str


# Response
class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    assigned_to: int
    category: str
    message: str
    reply: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True