from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from backend.app.app.models import ExamUsers


username_pattern = re.compile(r"^user([1-9]|[1-4][0-9]|50)$")
password_pattern = re.compile(r"^User@\d{4}$")

#user-login
def login_user(db: Session, username: str, password: str):
    user = db.query(ExamUsers).filter(ExamUsers.username == username).first()

    # If user NOT exists → create new user
    if not user:
        user = ExamUsers(
            username=username,
            password=password
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # If exists → check password
    if user.password != password:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return user


#  STORE name + email
def create_user_details(db: Session, user_id: int, name: str, email: str):
    user = db.query(ExamUsers).filter(ExamUsers.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = name
    user.email = email

    db.commit()
    db.refresh(user)

    return user


#  GET USER
def get_user(db: Session, user_id: int):
    user = db.query(ExamUsers).filter(ExamUsers.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
