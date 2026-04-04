from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.api.deps import get_db, get_current_user
from backend.app.app.crud.Exam_question_crud import evaluate_code, get_all_questions,evaluate_test,create_test, get_tech_questions_service, get_user_submissions, run_code_service, submit_code_service
from backend.app.app.models.Coding_questions import Coding_Questions
from backend.app.app.models.Exam_questions import Questions
from backend.app.app.models.Submit_coding import Coding_Submissions
from backend.app.app.schemas.Exam_question_schemas import QuestionOut, ResultOut, RunCodeRequest, SubmitTest, TestCreate, SubmitCodeSchema

# router = APIRouter(tags=["Questions"])

# @router.get("/api/questions/{assessment_id}")
# def get_questions(assessment_id: int, db: Session = Depends(get_db)):

#     try:
#         return QuestionsCrud(db).get_questions(assessment_id)
#     except Exception as e:
#         return {"error": str(e)}


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
def run_code(payload: RunCodeRequest, db: Session = Depends(get_db)):
    return run_code_service(payload)

@router.post("/test/submit-code")
def submit_code(payload: SubmitCodeSchema, db: Session = Depends(get_db)):
    return submit_code_service(db, payload)

@router.get("/test/submissions/{user_id}")
def fetch_submissions(user_id: int, db: Session = Depends(get_db)):
    return get_user_submissions(db, user_id)

# @router.post("/submit", response_model=ResultOut)
# def submit_test(payload: SubmitTest, db: Session = Depends(get_db)):

#     score = evaluate_test(db, payload.answers)
#     total = len(payload.answers)

#     return {
#         "score": score,
#         "total": total,
#         "passed": score >= 18   # configurable later
#     }

# @router.post("/submit-code")
# def submit_code(question_id: int, code: str, db: Session = Depends(get_db)):

#     question = db.query(Questions).filter(
#         Questions.question_id == question_id
#     ).first()

#     if not question:
#         return {"error": "Question not found"}

#     test_cases = db.query(Coding_Questions).filter(
#         Coding_Questions.question_id == question_id
#     ).all()

#     result = evaluate_code(code, test_cases)

#     # -------------------------
#     # SAVE SUBMISSION 
#     # -------------------------
#     submission = Coding_Submissions(
#         question_id=payload.question_id,
#         code=payload.code,
#         passed=result.get("passed", 0),   # FIX HERE
#         total=result.get("total", 0),
#         status="PASS" if result.get("passed", 0) == result.get("total", 0) else "FAIL"
#     )

#     db.add(submission)
#     db.commit()
#     return result