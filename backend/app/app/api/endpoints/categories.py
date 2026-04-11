from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.Categories_crud import CategoriesCrud, AssessmentCrud
from backend.app.app.schemas.mentor_categories_schema import (
    AssessmentTypeCreate,       # FIX: was Assesment_Type (typo + wrong name)
    CategoryCreate,
    AssessmentCreate,
    AssessmentMarksSubmit,
    SaveAssessmentSchema,  
            # NEW: needed for marks submission endpoint
)

router = APIRouter(prefix="/mentor_assesment", tags=["Mentor_Assessments"])  # FIX: renamed prefix — this router handles more than just categories

@router.get("/assessment/intern")
def get_intern_details(
    name: str,
    batch: str,
    db: Session = Depends(get_db)
):
    return AssessmentCrud(db).get_intern_by_name_batch(name, batch)

@router.post("/types")
def create_assessment_type(
    data: AssessmentTypeCreate,
    current_user=Depends(role_required([4])),
    db: Session = Depends(get_db),
):
    return AssessmentCrud(db).create_assessment_type(data, current_user)


@router.get("/asssesment_types")   # FIX: was /types — changed to be more consistent with the route naming
def get_assessment_types(
    assessment_type_id: Optional[int] = None,   # NEW: optional filter by type
    db: Session = Depends(get_db),
):
    return AssessmentCrud(db).get_all_assessment_types(assessment_type_id)

# ═══════════════════════════════════════════════════════
#  CATEGORIES
# ═══════════════════════════════════════════════════════

@router.post("/categories")
def create_category(
    payload: CategoryCreate,
    current_user=Depends(role_required([4])),
    db: Session = Depends(get_db),
):
    return CategoriesCrud(db).create_category(payload, current_user)


@router.get("/categories")
def get_categories(
    assessment_type_id: Optional[int] = None,   # NEW: optional filter by type
    db: Session = Depends(get_db),
):
    return CategoriesCrud(db).get_all_categories(assessment_type_id)


# ═══════════════════════════════════════════════════════
#  ASSESSMENTS
# ═══════════════════════════════════════════════════════

# @router.post("/")
# def create_assessment(
#     data: AssessmentCreate,
#     current_user=Depends(role_required([4])),
#     db: Session = Depends(get_db),
# ):
#     return AssessmentCrud(db).create_assessment(data, current_user)


@router.get("/")
def get_all_assessments(
    intern_id: Optional[int] = None,    # NEW: expose the filters your CRUD already supports
    mentor_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return AssessmentCrud(db).get_all_assessments(intern_id, mentor_id)


@router.get("/{assessment_id}")
def get_assessment_by_id(
    assessment_id: int,
    # current_user=Depends(role_required([1, 4])),  # FIX: was role 4 only — comment said change to 1
    db: Session = Depends(get_db),
):
    return AssessmentCrud(db).get_assessment_by_id(assessment_id)


# ═══════════════════════════════════════════════════════
#  MARKS SUBMISSION  — was missing entirely
# ═══════════════════════════════════════════════════════

# @router.post("/{assessment_id}/marks")
# def add_assessment_marks(
#     assessment_id: int,
#     body: AssessmentMarksSubmit,
#     current_user=Depends(role_required([4])),
#     db: Session = Depends(get_db),
# ):
#     marks_list = [item.dict() for item in body.category_marks]
#     return AssessmentCrud(db).add_assessment_marks(assessment_id, marks_list, current_user)


# @router.get("/intern/{intern_id}/summary")
# def get_intern_summary(
#     intern_id: int,
#     db: Session = Depends(get_db),
# ):
#     return AssessmentCrud(db).get_intern_assessment_summary(intern_id)

@router.post("/assessment/save")
def save_assessment(data: SaveAssessmentSchema, db: Session = Depends(get_db), current_user=Depends(role_required([4]) )):
    return AssessmentCrud(db).save_assessment(data, current_user)
