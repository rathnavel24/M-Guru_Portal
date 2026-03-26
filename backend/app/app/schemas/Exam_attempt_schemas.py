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