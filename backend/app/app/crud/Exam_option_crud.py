from sqlalchemy.orm import Session
from backend.app.app.models.Exam_options import Options

class OptionsCrud:
    def __init__(self, db:Session):
        self.db = db

    def get_options(self, question_id: int):
        return self.db.query(Options).filter(
            Options.question_id == question_id
        ).all()
       