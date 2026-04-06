from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db, get_current_user
from backend.app.app.crud.Exam_attempt_crud import AttemptCrud
from backend.app.app.crud.Exam_question_crud import evaluate_code, get_all_questions,evaluate_test,create_test, get_tech_questions_service, get_user_submissions, run_code, run_code_judge0, submit_code_service, submit_code_service_judge0
from backend.app.app.models.Coding_questions import Coding_Questions
from backend.app.app.models.Exam_questions import Questions
from backend.app.app.models.Submit_coding import Coding_Submissions
from backend.app.app.schemas.Exam_question_schemas import QuestionOut, ResultOut, RunCodeRequest, RunCodeResponse, SubmitCodeRequest, SubmitCodeSchema, SubmitTest, TestCreate


router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/questions", response_model=list[QuestionOut])
def get_apti_questions(db: Session = Depends(get_db)):

    return get_all_questions(db)

##########

@router.post("/upload",summary="Upload Questions",description="Insert questions into database")
def upload_questions(payload: TestCreate, db: Session = Depends(get_db)):
    return create_test(db, payload)

@router.get("/tech-questions")
def get_tech_questions(db: Session = Depends(get_db)):
    return get_tech_questions_service(db)

@router.post("/test/run-code")
def run_code_service(payload: RunCodeRequest, db: Session = Depends(get_db)):
    return run_code(payload.code, payload.input_data, payload.language)

@router.post("/test/submit-code/{user_id}")
def submit_code(user_id:int,payload: SubmitCodeSchema, db: Session = Depends(get_db)):
    return submit_code_service(db,user_id,payload)

@router.get("/test/submissions/{user_id}")
def fetch_submissions(user_id: int, db: Session = Depends(get_db)):
    return get_user_submissions(db, user_id)


# -------------------------
# RUN CODE
# -------------------------
@router.post("/test/run")
def run_code_api(payload: RunCodeRequest):

    return run_code_judge0(
        payload.code,
        payload.language,
        payload.input_data
    )


# -------------------------
# SUBMIT CODE
# -------------------------
@router.post("/test/submit/{user_id}")
def submit_code_api(
    user_id: int,
    payload: SubmitCodeRequest,
    db: Session = Depends(get_db)
):
    

    return submit_code_service_judge0(
        db,
        user_id,
        payload.dict()
    )