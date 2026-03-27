from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.crud.Exam_question_crud import get_all_questions,evaluate_test,create_test
from backend.app.app.schemas.Exam_question_schemas import *

# router = APIRouter(tags=["Questions"])

# @router.get("/api/questions/{assessment_id}")
# def get_questions(assessment_id: int, db: Session = Depends(get_db)):

#     try:
#         return QuestionsCrud(db).get_questions(assessment_id)
#     except Exception as e:
#         return {"error": str(e)}


router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/questions", response_model=list[QuestionOut])
def get_questions(db: Session = Depends(get_db)):

    return get_all_questions(db)

@router.post("/submit", response_model=ResultOut)
def submit_test(payload: SubmitTest, db: Session = Depends(get_db)):

    score = evaluate_test(db, payload.answers)

    total = len(payload.answers)

    return {
        "score": score,
        "total": total,
        "passed": score >= 18   # configurable later
    }

@router.post(
    "/upload",
    summary="Upload Questions",
    description="Insert questions into database"
)
def upload_questions(payload: TestCreate, db: Session = Depends(get_db)):
    return create_test(db, payload)