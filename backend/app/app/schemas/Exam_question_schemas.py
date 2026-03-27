from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id : int
    question_text : str
    section_id : int
    level : str
    marks : int

 

    class Config:
        from_attributes = True
################################

from pydantic import BaseModel
from typing import List


class OptionOut(BaseModel):
    id: int
    label: str
    text: str

    class Config:
        from_attributes = True


class QuestionOut(BaseModel):
    id: int
    question: str
    section: str
    options: List[OptionOut]

    class Config:
        from_attributes = True


class AnswerInput(BaseModel):
    question_id: int
    option_id: int


class SubmitTest(BaseModel):
    answers: List[AnswerInput]

class ResultOut(BaseModel):
    score: int
    total: int
    passed: bool

from pydantic import BaseModel
from typing import List


class QuestionCreate(BaseModel):
    section: str
    q: str
    opts: List[str]
    ans: int  


class TestCreate(BaseModel):
    name:str
    questions: List[QuestionCreate]

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "section": "QUANT/REACT/PYTHON",
                        "q": "QUESTION",
                        "opts": ["A","B","C","D"],
                        "ans": 1
                    }
                ]
            }
        }
