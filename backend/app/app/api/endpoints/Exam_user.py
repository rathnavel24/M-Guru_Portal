from fastapi import APIRouter, Depends
from backend.app.app.schemas.Exam_user_schemas import SignUpRequest,LoginRequest
from sqlalchemy.orm import Session
from backend.app.app.crud.Exam_user_crud import ExamSignUpDetails,ExamLoginDetails
from backend.app.app.api.deps import get_db
router = APIRouter(tags=["Portal_login"])

@router.post("/portal_signup")
async def signup(user_data:SignUpRequest,db:Session=Depends(get_db)):
    try:
        return ExamSignUpDetails(db, user_data).user_signup()
    except Exception as e:
        raise e

@router.post("/portal_login")
async def login(user_data:LoginRequest, db: Session=Depends(get_db)):
    try:
        return ExamLoginDetails(db,user_data).user_login()
    except Exception as e:
        raise e