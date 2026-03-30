from pydantic import BaseModel

class AssessmentResponse(BaseModel):
    assessment_id : int 
    name : str
    total_questions : int
    duration_minutes : int 
    pass_mark : int

    class Config:
        from_attributes = True
