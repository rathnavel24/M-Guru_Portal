from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.app.models.Exam_attempt import Attempts

class AttemptCrud:
    def __init__(self, db: Session):
        self.db = db

    def start_attempt(self, user_id: int, assessment_id: int):
        attempt = Attempts(
            user_id = user_id,
            assessment_id = assessment_id,
            started_at = datetime.utcnow(),
            status = "in_progress"
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt
    
    def submit_test(self, attempt_id: int):
        attempt = self.db.query(Attempts).filter(
            Attempts.attempt_id == attempt_id
        ).first()

        if not attempt:
            return{"error": "Attempt not found"}

        attempt.submitted_at = datetime.utcnow()
        attempt.status = "completed"

        self.db.commit()
        return attempt
    
    def get_result(self, attempt_id: int):
        attempt = self.db.query(Attempts).filter(
            Attempts.attempt_id == attempt_id
        ).first()

        if not attempt:
            return {"error": "Attempt not found"} 
        
        return attempt

    
    def get_attempt_history(self, user_id: int):
        return self.db.query(Attempts).filter(
            Attempts.user_id == user_id
        ).all()