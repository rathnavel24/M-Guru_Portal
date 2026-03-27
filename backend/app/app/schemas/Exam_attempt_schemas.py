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
    test_type: str | None = None
    correct_answers: int
    wrong_answers: int
    skipped_answers: int
    total_questions: int
    score: int
    percentage: int
    time_taken: int
    aptitude_score: int = 0
    technical_score: int = 0