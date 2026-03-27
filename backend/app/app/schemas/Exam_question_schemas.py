from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id : int
    question_text : str
    section_id : int
    level : str
    marks : int

 

    class Config:
        from_attributes = True
