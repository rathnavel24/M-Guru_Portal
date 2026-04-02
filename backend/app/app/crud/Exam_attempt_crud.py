from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.app.app.models.Exam_attempt import Attempts
from backend.app.app.models import Answers, Options

"""
USERFLOW 

START ATTEMPT
SAVE ANSWER
SUBMITE TEST
GET RESULT

(IF DATA FROM DB)

"""

"""
FROM FROMNTEND MEANS

ONLY

SUBMIT FINAL RESULT API

"""


class AttemptCrud:
    def __init__(self, db: Session):
        self.db = db


    def start_attempt(self, user_id: int, assessment_id: int):
         

        existing_attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id,
            Attempts.assessment_id == assessment_id,
            Attempts.status == "completed"
        ).first()

        if existing_attempt:
            return {"error": "You have already completed this test"}

        in_progress_attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id,
            Attempts.assessment_id == assessment_id,
            Attempts.status == "in_progress"
        ).first()

        if in_progress_attempt:
            return {
                "message": "Resume your test",
                "attempt_id": in_progress_attempt.attempt_id
            }

        attempt = Attempts(
            user_id=user_id,
            assessment_id=assessment_id,
            started_at=datetime.utcnow(),
            status="in_progress"
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return attempt
    def submit_test(self, user_id: int):

        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id,
            Attempts.status == "in_progress"
        ).order_by(Attempts.started_at.desc()).first()

        #  check if attempt exists
        if not attempt:
            return {"error": "No active attempt found"}

        answers = self.db.query(Answers).filter(
            Answers.attempt_id == attempt.attempt_id
        ).all()

        aptitude_correct = 0
        technical_correct = 0
        wrong = 0
        skipped = 0

        for ans in answers:

            # skipped
            if ans.is_skipped:
                skipped += 1
                continue

            options = self.db.query(Options).filter(
                Options.question_id == ans.question_id
            ).order_by(Options.option_id.asc()).all()

            # safety check
            if not options:
                continue

            selected_option_id = None

            # reconstruct index from stored option_id
            for idx, opt in enumerate(options):
                if opt.option_id == ans.selected_option_id:
                    selected_option_id = opt.option_id
                    break

            # -------------------------------------------------
            # STEP 3: get correct option (BY OPTION ID)
            # -------------------------------------------------
            correct_option = self.db.query(Options).filter(
                Options.question_id == ans.question_id,
                Options.is_correct == True
            ).first()

            # -------------------------------------------------
            # STEP 4: CHECK
            # -------------------------------------------------
            if correct_option and ans.selected_option_id == correct_option.option_id:

                if attempt.assessment_id == 1:
                    aptitude_correct += 1
                else:
                    technical_correct += 1
            else:
                wrong += 1

        total_questions = 30

        total_score = aptitude_correct + technical_correct
        percentage = (total_score / total_questions) * 100 if total_questions else 0

        # update attempt
        attempt.aptitude_score = aptitude_correct
        attempt.technical_score = technical_correct
        attempt.total_score = total_score
        attempt.total_percentage = int(percentage)
        attempt.submitted_at = datetime.utcnow()
        attempt.status = "completed"

        self.db.commit()
        self.db.refresh(attempt)

        return {
            "test_type": attempt.att_assessment.name,
            "aptitude_score": aptitude_correct,
            "technical_score": technical_correct,
            "correct_answers": total_score,
            "wrong_answers": wrong,
            "skipped_answers": skipped,
            "total_questions": total_questions,
            "score": total_score,
            "percentage": int(percentage),
            "time_taken": int(
                (attempt.submitted_at - attempt.started_at).total_seconds()
            )
        }
    # ---------------------------
    # HISTORY
    # ---------------------------
    def get_attempt_history(self, user_id: int):
        return self.db.query(Attempts).filter(
            Attempts.user_id == user_id
        ).all()

    # ---------------------------
    # RESULT (LATEST COMPLETED)
    # ---------------------------
    def get_result(self, user_id: int):

        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id,
            Attempts.status == "completed"
        ).order_by(Attempts.submitted_at.desc()).first()

        if not attempt:
            return {"error": "No completed attempt found"}

        answers = self.db.query(Answers).filter(
            Answers.attempt_id == attempt.attempt_id
        ).all()

        correct = 0
        wrong = 0
        skipped = 0

        for ans in answers:

     
            if ans.is_skipped:
                skipped += 1
                continue

            
            options = self.db.query(Options).filter(
                Options.question_id == ans.question_id
            ).order_by(Options.option_id.asc()).all()

            if not options:
                wrong += 1
                continue

        
            selected_option = next(
                (opt for opt in options if opt.option_id == ans.selected_option_id),
                None
            )

            if not selected_option:
                wrong += 1
                continue

          
            correct_option = next(
                (opt for opt in options if opt.is_correct),
                None
            )

            if correct_option and selected_option.option_id == correct_option.option_id:
                correct += 1
            else:
                wrong += 1

        total_questions = attempt.att_assessment.total_questions

        return {
            "test_type": attempt.att_assessment.name,
            "aptitude_score": attempt.aptitude_score,
            "technical_score": attempt.technical_score,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "skipped_answers": skipped,
            "total_questions": total_questions,
            "score": attempt.total_score,
            "percentage": attempt.total_percentage,
            "time_taken": int(
                (attempt.submitted_at - attempt.started_at).total_seconds()
            )
        }
    


    def save_result_from_frontend(self, user_id: int, data: dict):
        existing_attempt = (
            self.db.query(Attempts)
            .filter(Attempts.user_id == user_id)
            .first()
        )

        if existing_attempt:
            raise HTTPException(
                status_code=400,
                detail="User has already attempted the exam"
            )
        attempt = Attempts(
            user_id=user_id,
            assessment_id=data.get("assessment_id", 1),
            started_at=datetime.utcnow() - timedelta(seconds=data.get("time_taken", 0)),
            submitted_at=datetime.utcnow(),
            status="completed",
            aptitude_score=data.get("aptitude_score", 0),
            technical_score=data.get("technical_score", 0),
            total_score=data.get("score", 0),
            total_percentage=data.get("percentage", 0),
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return {

            "aptitude_score": data.get("aptitude_score", 0),
            "technical_score": data.get("technical_score", 0),
            "correct_answers": data.get("correct_answers", 0),
            "wrong_answers": data.get("wrong_answers", 0),
            "skipped_answers": data.get("skipped_answers", 0),
            "total_questions": data.get("total_questions", 0),
            "score": data.get("score", 0),
            "percentage": data.get("percentage", 0),
            "time_taken": data.get("time_taken", 0)
        }