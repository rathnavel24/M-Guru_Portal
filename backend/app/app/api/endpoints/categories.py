from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.Categories_crud import CategoriesCrud, AssessmentCrud,DashboardCrud
from backend.app.app.schemas.mentor_categories_schema import (
    AssessmentTypeCreate,
    CategoryCreate,
    SaveAssessmentSchema,
)

router = APIRouter(
    prefix="/mentor_assessment",
    tags=["Mentor Assessments"]
)

@router.get("/dashboard")
def get_dashboard(
    batch: str = None,  # ← optional batch filter
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return DashboardCrud(db).get_dashboard(
        mentor_id=current_user["user_id"],
        batch=batch
    )
# ═══════════════════════════════════════════════════════
# INTERN FETCH (Frontend types name + batch)
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════
# INTERN FETCH (Admin + Mentor)
# ═══════════════════════════════════════
@router.get("/intern")
def get_intern_details(
    name: str,
    batch: str,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_intern_by_name_batch(name, batch)


# ═══════════════════════════════════════
# ASSESSMENT TYPES
# ═══════════════════════════════════════

#  Create (Mentor only)
@router.post("/types")
def create_assessment_type(
    data: AssessmentTypeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([4]))
):
    return AssessmentCrud(db).create_assessment_type(data, current_user)


#  Get (Admin + Mentor)
@router.get("/types")
def get_assessment_types(
    assessment_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_all_assessment_types(assessment_type_id)


# ═══════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════

#  Create (Mentor only)
@router.post("/categories")
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([4]))
):
    return CategoriesCrud(db).create_category(payload, current_user)


#  Get (Admin + Mentor)
@router.get("/categories")
def get_categories(
    assessment_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return CategoriesCrud(db).get_all_categories(assessment_type_id)


# ═══════════════════════════════════════
# ASSESSMENTS
# ═══════════════════════════════════════

#  Mentor only - Get OWN assessments
@router.get("/my")
def get_my_assessments(
    db: Session = Depends(get_db),
    current_user=Depends(role_required([4]))
):
    return AssessmentCrud(db).get_all_assessments(
        mentor_id=current_user["user_id"]
    )

# Mentor only - Get OWN assessments (batch filter)
@router.get("/my/batch")
def get_my_assessments_by_batch(
    batch: str,   # ✅ required filter
    db: Session = Depends(get_db),
    current_user=Depends(role_required([4]))
):
    return AssessmentCrud(db).get_all_assessments(
        mentor_id=current_user["user_id"],
        batch=batch   # ✅ using existing CRUD
    )


#  Admin only - Get ALL assessments
@router.get("/all")
def get_all_assessments(
    intern_id: Optional[int] = None,
    mentor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1]))
):
    return AssessmentCrud(db).get_all_assessments(intern_id, mentor_id)


#  Admin + Mentor - Get by ID
# Mentor → only their data
# Admin → all data
@router.get("/{assessment_id}")
def get_assessment_by_id(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([1, 4]))
):
    return AssessmentCrud(db).get_assessment_by_id(
        assessment_id,
        current_user
    )


# ═══════════════════════════════════════
# SAVE ASSESSMENT
# ═══════════════════════════════════════

#  Mentor only - Create / Update assessment
@router.post("/save")
def save_assessment(
    data: SaveAssessmentSchema,
    db: Session = Depends(get_db),
    current_user=Depends(role_required([4]))
):
    return AssessmentCrud(db).save_assessment(data, current_user)



# @router.get("/dashboard")
# def get_dashboard(
#     db: Session = Depends(get_db),
#     current_user=Depends(role_required([1, 4]))
# ):
#     return DashboardCrud(db).get_dashboard(
#         mentor_id=current_user["user_id"]
#     )