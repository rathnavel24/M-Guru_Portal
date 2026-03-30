from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.Exam_assessment_crud import AssessmentCrud
from backend.app.app.schemas.Exam_assessment_schemas import AssessmentResponse

router = APIRouter(tags=["Assessments"])

@router.get("/tests", response_model=list[AssessmentResponse])
def get_tests(db: Session = Depends(get_db)):
    try:
        data = AssessmentCrud(db).get_assessments()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    