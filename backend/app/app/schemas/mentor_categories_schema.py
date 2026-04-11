from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ═══════════════════════════════════════
#  ASSESSMENT TYPE
# ═══════════════════════════════════════

class AssessmentTypeCreate(BaseModel):
    assessment_name: str

class AssessmentTypeResponse(BaseModel):
    assessment_type_id: int
    assessment_name: str
    status: int

    class Config:
        orm_mode = True


# ═══════════════════════════════════════
#  CATEGORY
# ═══════════════════════════════════════

class CategoryCreate(BaseModel):
    assessment_type_id: int   # FIX: was 'assessment_id' — must match CRUD & DB column
    category_name: str
    total_marks: int

class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    total_marks: Optional[int] = None   # added — useful to have

class CategoryResponse(BaseModel):
    category_id: int
    category_name: str
    total_marks: int
    assessment_type: Optional[str] = None
    assessment_type_id: Optional[int] = None

    class Config:
        orm_mode = True


# ═══════════════════════════════════════
#  ASSESSMENT
# ═══════════════════════════════════════
class AssessmentDetailCreate(BaseModel):
    category_id: int
    obtained_marks: int
    task_details: Optional[str] = None

class AssessmentCreate(BaseModel):
    assessment_type_id: int
    intern_id: int
    mentor_id: int

    remarks: Optional[str] = None
    task_details: Optional[str] = None

    details: list[AssessmentDetailCreate]
    # FIX: removed category_id  — categories are handled separately via marks
    # FIX: removed obtained_marks — marks are submitted via AssessmentMarksSubmit, not here

class AssessmentResponse(BaseModel):
    assessment_id: int
    assessment_type: Optional[str] = None
    intern_id: int
    intern_name: Optional[str] = None
    mentor_id: int
    mentor_name: Optional[str] = None
    remarks: Optional[str] = None
    task_details: Optional[str] = None
    total_obtained: Optional[int] = None
    total_marks: Optional[int] = None
    percentage: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ═══════════════════════════════════════
#  MARKS SUBMISSION  (for add_assessment_marks)
# ═══════════════════════════════════════

class CategoryMarkItem(BaseModel):
    category_id: int
    marks: int

class AssessmentMarksSubmit(BaseModel):
    category_marks: List[CategoryMarkItem]


# ═══════════════════════════════════════
#  CATEGORY DETAIL  (inside assessment response)
# ═══════════════════════════════════════

class CategoryDetail(BaseModel):
    category_id: int
    category_name: str
    obtained_marks: Optional[int] = None
    total_marks: int


# ═══════════════════════════════════════
#  FULL ASSESSMENT DETAIL  (for get_assessment_by_id)
# ═══════════════════════════════════════

class AssessmentDetailResponse(BaseModel):
    assessment_id: int
    assessment_type: Optional[str] = None

    intern_id: int
    intern_name: Optional[str] = None
    specialization: Optional[str] = None
    batch: Optional[str] = None

    mentor_id: int
    mentor_name: Optional[str] = None

    remarks: Optional[str] = None
    task_details: Optional[str] = None

    total_obtained: int
    total_marks: int
    percentage: float

    categories: List[CategoryDetail]

    class Config:
        orm_mode = True


# ═══════════════════════════════════════
#  INTERN SUMMARY  (for get_intern_assessment_summary)
# ═══════════════════════════════════════

class AssessmentSummaryItem(BaseModel):
    assessment_id: int
    assessment_type: str
    mentor_name: Optional[str] = None
    remarks: Optional[str] = None
    task_details: Optional[str] = None
    total_obtained: int
    total_marks: int
    percentage: float
    categories: List[CategoryDetail]

class InternAssessmentSummary(BaseModel):
    intern_id: int
    intern_name: str
    specialization: Optional[str] = None
    batch: Optional[str] = None
    grand_total_obtained: int
    grand_total_marks: int
    grand_percentage: float
    assessments: List[AssessmentSummaryItem]



class CategoryMark(BaseModel):
    category_id: int
    marks: float


class SaveAssessmentSchema(BaseModel):
    intern_id: int
    mentor_id: int
    assessment_type_id: int
    assessment_date: Optional[datetime] = None

    remarks: Optional[str] = None
    task_details: Optional[str] = None

    category_marks: List[CategoryMark]