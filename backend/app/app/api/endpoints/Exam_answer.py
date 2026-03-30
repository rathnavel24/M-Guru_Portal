from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.Exam_attempt_crud import AttemptCrud
from backend.app.app.schemas.Exam_answer_schemas import ReviewResponse, SaveAnswerRequest
from backend.app.app.crud.Exam_answer_crud import AnswerCrud

router = APIRouter(tags=["Answer"])

@router.post("/save-answer")
def save_answer(payload: SaveAnswerRequest, db: Session = Depends(get_db)):

    crud = AnswerCrud(db)

    return crud.save_answer(
        attempt_id=payload.attempt_id,
        question_id=payload.question_id,
        option_index=payload.option_index,
        is_skipped=payload.is_skipped
    )
@router.get("/api/review/{attempt_id}")
def review_answers(attempt_id: int, db: Session = Depends(get_db)):

    try:
        return AnswerCrud(db).review_answer(attempt_id)
    except Exception as e:
        return {"error": str(e)}    