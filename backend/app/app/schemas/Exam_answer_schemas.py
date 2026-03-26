from pydantic import BaseModel
from typing import Optional

class SaveAnswer(BaseModel):
    attempt_id : int
    question_id : int
    option_id : Optional[int]
    is_skipped : bool

class ReviewResponse(BaseModel):
    question_id : int
    selected_option_id : int
    is_skipped : bool    

    class Config:
        from_attributes = True