from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.Categories_crud import CategoriesCrud, AssessmentCrud
from backend.app.app.schemas.mentor_categories_schema import (
    AssessmentTypeCreate,
    CategoryCreate,
    SaveAssessmentSchema,
)

router = APIRouter(
    prefix="/mentor_assessment",
    tags=["Mentor Assessments"]
)

# ═══════════════════════════════════════════════════════
# INTERN FETCH (Frontend types name + batch)
# ═══════════════════════════════════════════════════════

@router.get("/intern")
def get_intern_details(
    name: str,
    batch: str,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_intern_by_name_batch(name, batch)


# ═══════════════════════════════════════════════════════
# ASSESSMENT TYPES
# ═══════════════════════════════════════════════════════

@router.post("/types")
def create_assessment_type(
    data: AssessmentTypeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).create_assessment_type(data, current_user)


@router.get("/types")
def get_assessment_types(
    assessment_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_all_assessment_types(assessment_type_id)


# ═══════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════

@router.post("/categories")
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return CategoriesCrud(db).create_category(payload, current_user)


@router.get("/categories")
def get_categories(
    assessment_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return CategoriesCrud(db).get_all_categories(assessment_type_id)


# ═══════════════════════════════════════════════════════
# ASSESSMENTS
# ═══════════════════════════════════════════════════════

@router.get("/")
def get_all_assessments(
    intern_id: Optional[int] = None,
    mentor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_all_assessments(intern_id, mentor_id)


@router.get("/{assessment_id}")
def get_assessment_by_id(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_assessment_by_id(assessment_id)


# ═══════════════════════════════════════════════════════
# SAVE ASSESSMENT (MAIN API)
# ═══════════════════════════════════════════════════════

@router.post("/save")
def save_assessment(
    data: SaveAssessmentSchema,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).save_assessment(data, current_user)