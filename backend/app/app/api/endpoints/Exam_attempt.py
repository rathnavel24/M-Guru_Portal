from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.schemas.Exam_attempt_schemas import StartAttempt, SubmitTest
from backend.app.app.crud.Exam_attempt_crud import AttemptCrud

router = APIRouter(tags=["Attempts"])

@router.post("/api/start-attempt")
def start_attempt(data: StartAttempt, db:Session = Depends(get_db)):

    try:
        return AttemptCrud(db).start_attempt(data.user_id, data.assessment_id)
    except Exception as e:
        return {"error": str(e)}
    

@router.post("/api/submit-test")
def submit_test(data: SubmitTest, db: Session = Depends(get_db)):
    try:
        return AttemptCrud(db).submit_test(data.attempt_id)
    except Exception as e:
        return {"error": str(e)}

@router.get("/api/result/{attempt_id}")
def get_result(attempt_id: int, db: Session = Depends(get_db)):
    try:
        return AttemptCrud(db).get_result(attempt_id)
    except Exception as e:
        return {"error": str(e)}

@router.get("/api/attempts/{user_id}")
def get_attempts(user_id: int, db: Session = Depends(get_db)):
    try:
        return AttemptCrud(db).get_attempt_history(user_id)
    except Exception as e:
        return {"error": str(e)}
    

    