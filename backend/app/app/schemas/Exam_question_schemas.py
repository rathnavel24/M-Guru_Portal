from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id : int
    question_text : str
    section_id : int
    level : str
    marks : int

class OptionResponse(BaseModel):
    id : int
    question_id : int
    options_label : str
    option_text : str    
