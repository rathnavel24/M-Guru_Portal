from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.app.schemas.Exam_user_schemas import (
    LoginRequest,
    UserDetailsCreate,
    UserResponse
)
from backend.app.app.crud.Exam_user_crud import (
    login_user,
    create_user_details,
    get_user
)
from backend.app.app.api.deps import get_db
router = APIRouter(tags=["Portal_login"])

#  LOGIN
@router.post("/exam-login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = login_user(db, data.username, data.password)

    return {
        "message": "Login Successful",
        "user_id": user.user_id,
        "username": user.username
    }


#  STORE NAME + EMAIL
@router.post("/users/{user_id}/details", response_model=UserResponse)
def save_details(user_id: int, data: UserDetailsCreate, db: Session = Depends(get_db)):
    return create_user_details(db, user_id, data.name, data.email)


#  GET USER DATA
@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)
