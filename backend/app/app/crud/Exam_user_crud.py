from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from backend.app.app.schemas import Exam_user_schemas 
from backend.app.app.models import ExamUsers


username_pattern = re.compile(r"^user([1-9]|[1-4][0-9]|50)$")
password_pattern = re.compile(r"^User@\d{4}$")

       
class ExamLoginDetails:
    def __init__(self, db: Session, user_data: Exam_user_schemas):
        self.db = db
        self.user_data = user_data

        
  
    def user_login(self):
        username = self.user_data.username
        password = self.user_data.password

    
        if not username_pattern.match(username):
            raise HTTPException(status_code=400, detail="Invalid username (user1-user50 only)")

       
        if not password_pattern.match(password):
            raise HTTPException(status_code=400, detail="Invalid password")

       
        user = self.db.query(ExamUsers).filter(
            ExamUsers.username == username
        ).first()

        
        if not user:
            new_user = ExamUsers(
                username=username,
                password=password
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            return {
                "message": "User created & Login Successful",
                "user_id": new_user.user_id
            }

        if user.password != password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        return {
            "message": "Login Successful",
            "user_id": user.user_id
        }


class UserInfoService:
    def __init__(self, db: Session, data: Exam_user_schemas):
        self.db = db
        self.data = data

    def add_user_info(self):
        user = self.db.query(ExamUsers).filter(
            ExamUsers.user_id == self.data.user_id
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.name = self.data.name
        user.email = self.data.email

        self.db.commit()
        self.db.refresh(user)

        return {
            "message": "User info added successfully",
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email
        }