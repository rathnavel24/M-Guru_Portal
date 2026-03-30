from sqlalchemy.orm import Session
from backend.app.app.models.Exam_answer import Answers
from backend.app.app.models.Exam_options import Options


class AnswerCrud:

     def __init__(self, db: Session):
          self.db = db

     def save_answer(self, attempt_id: int, question_id: int, option_index: int, is_skipped: bool = False):

          options = self.db.query(Options).filter(
               Options.question_id == question_id
          ).order_by(Options.option_id.asc()).all()

          if not options:
               return {"error": "No options found"}

          if is_skipped:
               selected_option_id = None
          else:
               if option_index < 0 or option_index >= len(options):
                    return {"error": "Invalid option index"}

               selected_option_id = options[option_index].option_id

          existing = self.db.query(Answers).filter(
               Answers.attempt_id == attempt_id,
               Answers.question_id == question_id
          ).first()

          if existing:
               self.db.delete(existing)

          answer = Answers(
               attempt_id=attempt_id,
               question_id=question_id,
               selected_option_id=selected_option_id,
               is_skipped=is_skipped
          )

          self.db.add(answer)
          self.db.commit()

          return {"message": "Answer saved"}

     def review_answer(self, attempt_id: int):
          return self.db.query(Answers).filter(
               Answers.attempt_id == attempt_id
          ).all