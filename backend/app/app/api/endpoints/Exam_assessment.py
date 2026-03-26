from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
import backend.app.app.crud.Exam_assessment_crud as AssessmentCrud
from backend.app.app.schemas.Exam_assessment_schemas import AssessmentResponse

router = APIRouter(tags=["Assessments"])

@router.get("/tests")
def get_tests(db: Session = Depends(get_db)):
    try:
        return AssessmentResponse(db).get_assessments()
    except Exception as e:
        return{"error": str(e)}

    