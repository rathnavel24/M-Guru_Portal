from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    category_name: str


class CategoryCreate(CategoryBase):
    category_name: str
    total_marks: int
    


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    status: int

    class Config:
        orm_mode = True

class Assesment_Type(BaseModel):
    assessment_name: str

class AssessmentCreate(BaseModel):
    assessment_type_id: int
    category_id: int
    intern_id: int
    mentor_id: int
    remarks: Optional[str] = None
    task_details: Optional[str] = None
    obtained_marks: int