from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app import db
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.Categories_crud import CategoriesCrud,AssessmentCrud
from backend.app.app.schemas.mentor_categories_schema import AssessmentCreate, CategoryCreate,Assesment_Type

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(payload:CategoryCreate,
                    current_user = Depends(role_required([4])),
                    db: Session = Depends(get_db)):

    crud = CategoriesCrud(db)


    return crud.create_category(payload, current_user)


@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    return CategoriesCrud(db).get_all_categories()


@router.post("/create_assessment_type")
def create_assessment_type(
    data: Assesment_Type,
    current_user = Depends(role_required([4])),
    db: Session = Depends(get_db)):

    return AssessmentCrud(db).create_assessment_type(data, current_user)



@router.post("/create_assessment")
def create_assessment(
    data: AssessmentCreate,
    current_user = Depends(role_required([4])),
    db: Session = Depends(get_db)):

    return AssessmentCrud(db).create_assessment(data, current_user)


@router.get("/")
def get_all_assessments(db: Session = Depends(get_db)):
    return AssessmentCrud(db).get_all_assessments()


@router.get("/{assessment_id}")
def get_assessment_by_id(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    return AssessmentCrud(db).get_assessment_by_id(assessment_id)


@router.get("/{assessment_id}/full")
def get_assessment_with_categories(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    return AssessmentCrud(db).get_assessment_with_categories(assessment_id)

