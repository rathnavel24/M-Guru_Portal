from sqlalchemy.orm import Session
from backend.app.app.models.Exam_questions import Questions


class QuestionsCrud:

    def __init__(self, db: Session):
        self.db = db

    def get_questions(self, assessment_id: int):
        return self.db.query(Questions).filter(
            Questions.assessment_id == assessment_id
        ).all()
    