from fastapi import APIRouter, Depends
from backend.app.app.schemas.Exam_user_schemas import LoginRequest,UserInfoRequest
from sqlalchemy.orm import Session
from backend.app.app.crud.Exam_user_crud import ExamLoginDetails,UserInfoService
from backend.app.app.api.deps import get_db
router = APIRouter(tags=["Portal_login"])


@router.post("/user_login")
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    service = ExamLoginDetails(db, data)
    return service.user_login()
    
@router.post("/add_user_info")
def add_user_info(data: UserInfoRequest, db: Session = Depends(get_db)):
    service = UserInfoService(db, data)
    return service.add_user_info()