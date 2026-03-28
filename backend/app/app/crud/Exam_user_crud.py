from fastapi import HTTPException
import re
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.app.models import ExamUsers
from backend.app.app.models.Exam_attempt import Attempts


<<<<<<< HEAD
class ExamUserCRUD:

    def __init__(self, db: Session):
        self.db = db
=======
username_pattern = re.compile(r"^user([1-9]|[1-4][0-9]|50)$")
password_pattern = re.compile(r"^User@\d{4}$")
>>>>>>> 9099ffa45ce7d146ecebfaa98d603ded974cec66

    username_pattern = re.compile(r"^user([1-9]|[1-2][0-9]|30)$")
    password_pattern = re.compile(r"^User@\d{4}$")

    def login_user(self, username: str, password: str):
        user = self.db.query(ExamUsers).filter(ExamUsers.username == username).first()

        if not user:
            user = ExamUsers(
                username=username,
                password=password
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user

        if user.password != password:
            raise HTTPException(status_code=400, detail="Incorrect password")

        return user

    def create_user_details(self, user_id: int, name: str, email: str):
        user = self.db.query(ExamUsers).filter(ExamUsers.user_id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.name = name
        user.email = email

        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user(self, user_id: int):
        user = self.db.query(ExamUsers).filter(ExamUsers.user_id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    def get_user_results(self):

        subquery = (
            self.db.query(
                Attempts.user_id,
                func.max(Attempts.attempt_id).label("latest_attempt")
            )
            .group_by(Attempts.user_id)
            .subquery()
        )

        results = (
            self.db.query(
                Attempts.user_id,
                ExamUsers.username,
                Attempts.total_score,
                Attempts.total_percentage
            )
            .join(ExamUsers, ExamUsers.user_id == Attempts.user_id)
            .join(
                subquery,
                (Attempts.user_id == subquery.c.user_id) &
                (Attempts.attempt_id == subquery.c.latest_attempt)
            )
            .order_by(Attempts.user_id.asc())
            .all()
        )

<<<<<<< HEAD
        return [
            {
                "user_id": r.user_id,
                "username": r.username,
                "score": r.total_score,
                "percentage": r.total_percentage
            }
            for r in results
        ]

    def get_single_user_results(self, user_id: int):

        subquery = (
            self.db.query(
                Attempts.user_id,
                func.max(Attempts.attempt_id).label("latest_attempt")
            )
            .filter(Attempts.user_id == user_id)
            .group_by(Attempts.user_id)
            .subquery()
        )

        result = (
            self.db.query(
                Attempts.user_id,
                ExamUsers.username,
                Attempts.total_score,
                Attempts.total_percentage
            )
            .join(ExamUsers, ExamUsers.user_id == Attempts.user_id)
            .join(
                subquery,
                (Attempts.user_id == subquery.c.user_id) &
                (Attempts.attempt_id == subquery.c.latest_attempt)
            )
            .first()
        )

        if not result:
            raise HTTPException(status_code=404, detail="User not found or no attempts")

        return {
            "user_id": result.user_id,
            "username": result.username,
            "score": result.total_score,
            "percentage": result.total_percentage
        }
=======
    return user
>>>>>>> 9099ffa45ce7d146ecebfaa98d603ded974cec66
