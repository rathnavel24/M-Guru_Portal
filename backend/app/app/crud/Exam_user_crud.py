from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from backend.app.app.schemas import Exam_user_schemas 
from backend.app.app.models import ExamUsers


# users_db = {}

username_pattern = re.compile(r"^user([1-9]|[1-2][0-9]|30)$")
password_pattern = re.compile(r"^User@\d{4}$")


class ExamSignUpDetails:
    def __init__(self, db: Session, user_data:Exam_user_schemas):
        self.db = db
        self.user_data = user_data

    def user_signup(self):
        username = self.user_data.username
        password = self.user_data.password

        if not username_pattern.match(username):
            raise HTTPException(status_code=404, detail="Invalid username (use user1 to user30)")
        
        if not password_pattern.match(password):
            raise HTTPException(status_code=400, detail="Password must be like User@1234")
        
        existing_user = self.db.query(ExamUsers).filter(ExamUsers.username == username).first()

        if existing_user:
            raise HTTPException(status_code=400,detail="Username already exists")
        
        existing_password = self.db.query(ExamUsers).filter(ExamUsers.password == password).first()

        if existing_password:
            raise HTTPException(status_code=400,detail="Password already exists")
        
    
        new_user = ExamUsers(
            username = username,
            password = password
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        print("user inserted successfully")

        return {"message": "Signup Successful" , "user" : username}
       
        
       
class ExamLoginDetails:
    def __init__(self, db:Session, user_data:Exam_user_schemas):
        self.db = db
        self.user_data = user_data

    def user_login(self):
        username  = self.user_data.username
        password = self.user_data.password

        user = self.db.query(ExamUsers).filter(ExamUsers.username == username).first()

        if not user:
            raise HTTPException(status_code=400,detail="User not found")
        
        if user.password != password:
            raise HTTPException(status_code=400, detail="Incorrect password")
        
        return {"message" : "Login Successful", "user" : username}

# from backend.app.app.models import Attempts, ExamUsers

# def get_user_results(self):

#     results = (
#         self.db.query(
#             Attempts.user_id,
#             ExamUsers.username,
#             Attempts.total_score,
#             Attempts.total_percentage
#         )
#         .join(ExamUsers, ExamUsers.user_id == Attempts.user_id)
#         .all()
#     )

#     return [
#         {
#             "user_id": r.user_id,
#             "username": r.username,
#             "score": r.total_score,
#             "percentage": r.total_percentage
#         }
#         for r in results
#     ]