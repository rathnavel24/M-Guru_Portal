from pydantic import BaseModel

class AssessmentResponse(BaseModel):
    id : int 
    name : str
    total_questions : int
    duration_minutes : int 
    pass_mark : int
