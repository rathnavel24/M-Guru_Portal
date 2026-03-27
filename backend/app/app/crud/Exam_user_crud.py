from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from backend.app.app.schemas import Exam_user_schemas 
from backend.app.app.models import ExamUsers


username_pattern = re.compile(r"^user([1-9]|[1-2][0-9]|30)$")
password_pattern = re.compile(r"^User@\d{4}$")




class ExamLoginDetails:
    def __init__(self, db: Session, user_data: Exam_user_schemas):
        self.db = db
        self.user_data = user_data

    def user_login(self):
        username = self.user_data.username
        password = self.user_data.password
        email = getattr(self.user_data, "email", None)
        name = getattr(self.user_data, "name", None)

        user = self.db.query(ExamUsers).filter(ExamUsers.username == username).first()

    
        if not user:
            new_user = ExamUsers(
                username=username,
                password=password,
                email=email,
                name=name
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            return {
                "message": "New User Created & Login Successful",
                "user": username
            }

        if user.password != password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        if email:
            user.email = email
        if name:
            user.name = name

        self.db.commit()
        self.db.refresh(user)

        return {
            "message": "Login Successful",
            "user": username
        }