from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app import db
from backend.app.app.api.deps import get_db, role_required
from backend.app.app.crud.Exam_question_crud import get_all_coding_results, get_coding_result
from backend.app.app.schemas.Exam_attempt_schemas import FinalResultSchema, SaveScoreRequest, StartAttempt, SubmitTest
from backend.app.app.crud.Exam_attempt_crud import AttemptCrud

router = APIRouter(tags=["Attempts"])

@router.post("/start/{user_id}")
def start_attempt(user_id: int, db: Session = Depends(get_db)):
    return AttemptCrud(db).start_attempt(user_id)


@router.post("/save-scores/{user_id}")
def save_scores(
    user_id: int,
    data:  SaveScoreRequest
,
    db: Session = Depends(get_db)
):
    return AttemptCrud(db).save_result_from_frontend(user_id, data.dict())


@router.post("/submit/{user_id}")
def finalll_submit(user_id: int, db: Session = Depends(get_db)):
    return AttemptCrud(db).submit_test(user_id)



@router.get("/coding/result/{user_id}/{question_id}")
def coding_result(user_id: int, question_id: int, db: Session = Depends(get_db)):
    return get_coding_result(db, user_id, question_id)


@router.get("/coding/results/{user_id}")
def all_coding_results(user_id: int, db: Session = Depends(get_db)):
    return get_all_coding_results(db, user_id)


# @router.get("/api/result/{attempt_id}")
# def get_result(attempt_id: int, db: Session = Depends(get_db)):
#     try:
#         return AttemptCrud(db).get_result(attempt_id)
#     except Exception as e:
#         return {"error": str(e)}

# @router.get("/api/attempts/{user_id}")
# def get_attempts(user_id: int, db: Session = Depends(get_db)):
#     try:
#         return AttemptCrud(db).get_attempt_history(user_id)
#     except Exception as e:
#         return {"error": str(e)}

@router.post("/save-scores/{user_id}")
def save_scores(
    user_id: int,
    data: SaveScoreRequest,
    db: Session = Depends(get_db)
):
    return AttemptCrud(db).save_result_from_frontend(user_id, data.dict())


@router.get("/users/{user_id}/test-status")
def get_test_status(user_id: int, db: Session = Depends(get_db)):
    
    return AttemptCrud(db).get_user_exam_status(user_id)


@router.get("/exam-summary")
def exam_summary(db=Depends(get_db),current_user=Depends(role_required([1]))):
    return AttemptCrud(db).get_exam_summary()


@router.delete("/truncate-exam-users")
def truncate_exam_users(db=Depends(get_db)):
    return AttemptCrud(db).truncate_exam_users()
