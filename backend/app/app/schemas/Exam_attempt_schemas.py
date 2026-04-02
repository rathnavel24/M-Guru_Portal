from typing import Literal

from pydantic import BaseModel
from datetime import datetime

class StartAttempt(BaseModel):
    user_id : int 
    assessment_id : int

class AttemptResponse(BaseModel):
    attempt_id : int
    started_at : datetime 

    class Config:
        from_attributes = True

class SubmitTest(BaseModel):
    attempt_id : int

class ResultResponse(BaseModel):
    attempt_id : int
    score : int
    percentage : int
    status : str

    class Config:
        from_attributes = True


class AttemptHistoryResponse(BaseModel):
    id : int 
    assessment_id : int
    score : int
    percentage : int 
    status : str     

    class Config:
        from_attributes = True      


class FinalResultSchema(BaseModel):
    test_type: Literal["aptitude", "technical"]  #REQUIRED

    correct_answers: int
    wrong_answers: int
    skipped_answers: int
    total_questions: int

    score: int
    time_taken: int
