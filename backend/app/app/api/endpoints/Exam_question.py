from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.Exam_question_crud import QuestionsCrud
from backend.app.app.schemas.Exam_question_schemas import QuestionResponse

router = APIRouter(tags=["Questions"])

@router.get("/api/questions/{assessment_id}")
def get_questions(assessment_id: int, db: Session = Depends(get_db)):

    try:
        return QuestionsCrud(db).get_questions(assessment_id)
    except Exception as e:
        return {"error": str(e)}
    