from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.schemas.Exam_answer_schemas import SaveAnswer, ReviewResponse
from backend.app.app.crud.Exam_answer_crud import AnswerCrud

router = APIRouter(tags=["Answer"])

@router.post("/save-answer")
def save_answer(data: SaveAnswer, db: Session = Depends(get_db)):

    try:
        return AnswerCrud(db).save_answer(
            data.attempt_id,
            data.question_id,
            data.option_id,
            data.is_skipped
        )
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/api/review/{attempt_id}")
def review_answers(attempt_id: int, db: Session = Depends(get_db)):

    try:
        return AnswerCrud(db).review_answer(attempt_id)
    except Exception as e:
        return {"error": str(e)}    