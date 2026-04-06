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
                    "type": "mcq",
                    "section": "Quantitative",
                    "q": "2+2?",
                    "opts": ["3","4","5","6"],
                    "ans": 1
                    },
                    {
                    "type": "coding",
                    "section": "PYTHON",
                    "q": "Add two numbers",
                    "test_cases": [
                        {"input": "2 3", "output": "5"},
                        {"input": "10 20", "output": "30"}
                    ]
                    }
                ]
            }
        }
# {

from pydantic import BaseModel
from typing import List, Optional

# -------------------------
# Test Case Model (for coding)
# -------------------------
class TestCase(BaseModel):
    input: str
    output: str
    hidden:Optional[bool] = False

# -------------------------
# Question Model (common)
# -------------------------
class Question(BaseModel):
    type: str
    q: str
    section: str

    # MCQ fields (optional)
    opts: Optional[List[str]] = None
    ans: Optional[int] = None

    # Coding fields (optional)
    test_cases: Optional[List[TestCase]] = None

# -------------------------
# Main Request Model
# -------------------------
class TestCreate(BaseModel):
    name: str   # REQUIRED
    questions: List[Question]

# class RunCodeRequest(BaseModel):
#     code: str
#     input_data: str = ""
#     language: str = "python"
class SubmitCodeSchema(BaseModel):
    question_id: int
    code: str
    language: str


class SubmitCodeRequest(BaseModel):
    question_id: int
    code: str
    language: str



    #    "questions": [
#     {
#       "type": "mcq",
#       "section": "Quantitative",
#       "q": "2+2?",
#       "opts": ["3","4","5","6"],
#       "ans": 1
#     },
#     {
#       "type": "coding",
#       "section": "PYTHON",
#       "q": "Add two numbers",
#       "test_cases": [
#         {"input": "2 3", "output": "5"},
#         {"input": "10 20", "output": "30"}
#       ]
#     }
# #   ]
# }


###################################


class CodeSubmitRequest(BaseModel):
    question_id: int
    language: str
    code: str


class CodeSubmitResponse(BaseModel):
    question_id: int
    status: str
    passed: int
    total: int


class RunCodeRequest(BaseModel):
    code: str
    language: str
    input_data: Optional[str] = ""


class RunCodeResponse(BaseModel):
    output: Optional[str] = ""
    error: Optional[str] = None