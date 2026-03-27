from pydantic import BaseModel

class OptionResponse(BaseModel):
    option_id : int
    question_id : int
    option_label : str
    option_text : str

    class Config:
        from_attributes = True