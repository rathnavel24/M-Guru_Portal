from sqlalchemy.orm import Session 
from backend.app.app.models.Exam_assessment import Assessments

class AssessmentCrud:
    def __init__(self, db: Session):
        self.db = db

def get_assessments(self):
    return self.db.query(Assessments).all()
