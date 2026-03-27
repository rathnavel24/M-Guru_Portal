from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db
from backend.app.app.schemas.Exam_attempt_schemas import FinalResultSchema, StartAttempt, SubmitTest
from backend.app.app.crud.Exam_attempt_crud import AttemptCrud

router = APIRouter(tags=["Attempts"])

@router.post("/api/start-attempt")
def start_attempt(data: StartAttempt, db:Session = Depends(get_db)):

    try:
        return AttemptCrud(db).start_attempt(data.user_id, data.assessment_id)
    except Exception as e:
        return {"error": str(e)}

# @router.post("/api/submit-test")
# def submit_test(data: SubmitTest, db: Session = Depends(get_db)):
#     try:
#         return AttemptCrud(db).submit_test(data.attempt_id)
#     except Exception as e:
#         return {"error": str(e)}

# @router.get("/api/result/{attempt_id}")
# def get_result(attempt_id: int, db: Session = Depends(get_db)):
#     try:
#         return AttemptCrud(db).get_result(attempt_id)
#     except Exception as e:
#         return {"error": str(e)}

@router.get("/api/attempts/{user_id}")
def get_attempts(user_id: int, db: Session = Depends(get_db)):
    try:
        return AttemptCrud(db).get_attempt_history(user_id)
    except Exception as e:
        return {"error": str(e)}
    

@router.post("/submit-test/{user_id}")
def submit_test(user_id: int, db: Session = Depends(get_db)):
    return AttemptCrud(db).submit_test(user_id)

@router.get("/result/{user_id}")
def get_result(user_id: int, db: Session = Depends(get_db)):
    return AttemptCrud(db).get_result(user_id)

@router.post("/submit-final-result/{user_id}")
def submit_final_result(
    user_id: int,
    data: FinalResultSchema,
    db: Session = Depends(get_db)
):
    service = AttemptCrud(db)
    return service.save_result_from_frontend(user_id, data.dict())