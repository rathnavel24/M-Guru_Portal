from sqlalchemy.orm import Session
from backend.app.app.models.Exam_answer import Answers

class AnswerCrud:
     def __init__(self, db: Session):
          self.db = db

     def save_answer(self, attempt_id: int, question_id: int, option_id: int, is_skipped: bool): 
          answer = Answers(
               attempt_id = attempt_id,
               question_id = question_id,
               selected_option_id  = option_id,
               is_skipped = is_skipped
          )    

          self.db.add(answer)
          self.db.commit()
          return {"message": "Answer saved"}
     
     def review_answer(self, attempt_id: int):
          return self.db.query(Answers).filter(
               Answers.attempt_id == attempt_id
          ).all