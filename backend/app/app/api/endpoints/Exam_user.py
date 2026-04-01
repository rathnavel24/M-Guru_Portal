from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# from backend.app.app.crud.email_services import check_and_notify
from backend.app.app.schemas.Exam_user_schemas import (
    LoginRequest,
    UserDetailsCreate,
    UserResponse
)
from backend.app.app.crud.Exam_user_crud import ExamUserCRUD
from backend.app.app.api.deps import get_db

router = APIRouter(prefix="/users", tags=["Portal_login"])

# ##########

# @router.get("/test-email")
# def test_email(db: Session = Depends(get_db)):
#     check_and_notify(db)
#     return {"message": "Alert mail sent to Students to complete exam"}
# ######


@router.post("/exam-login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    service = ExamUserCRUD(db)
    user = service.login_user(data.username, data.password)

    return {
        "message": "Login Successful",
        "user_id": user.user_id,
        "username": user.username
    }


@router.post("/{user_id}/details", response_model=UserResponse)
def save_details(user_id: int, data: UserDetailsCreate, db: Session = Depends(get_db)):
    service = ExamUserCRUD(db)
    return service.create_user_details(user_id, data.name, data.email)

@router.get("/results")
def get_user_results_endpoint(db: Session = Depends(get_db)):
    service = ExamUserCRUD(db)
    return service.get_user_results()


@router.get("/{user_id}/results")
def get_singleuser_results_endpoint(user_id: int, db: Session = Depends(get_db)):
    service = ExamUserCRUD(db)
    return service.get_single_user_results(user_id)

@router.get("/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    service = ExamUserCRUD(db)
    return service.get_user(user_id)

