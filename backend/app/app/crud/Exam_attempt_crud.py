from fastapi import HTTPException
from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session, aliased
from datetime import datetime, timedelta

from yaml import Mark
from backend.app.app.models.Exam_assessment import Assessments
from backend.app.app.models.Exam_attempt import Attempts
from backend.app.app.models import Answers, Options
from backend.app.app.models.Exam_user import ExamUsers

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
        
        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id
        ).first()

        if not attempt:
            raise HTTPException(404, "No attempt found. Submit sections first")

        # Update based on test_type
        test_type = data.get("test_type")

        if test_type == "aptitude":

            if attempt.aptitude_score is not None:
                raise HTTPException(400, "Aptitude already submitted")

            attempt.aptitude_score = data.get("score", 0)
            attempt.aptitude_correct = data.get("correct_answers", 0)
            attempt.aptitude_wrong = data.get("wrong_answers", 0)
            attempt.aptitude_skipped = data.get("skipped_answers", 0)

        elif test_type == "technical":

            if attempt.technical_score is not None:
                raise HTTPException(400, "Technical already submitted")

            attempt.technical_score = data.get("score", 0)
            attempt.technical_correct = data.get("correct_answers", 0)
            attempt.technical_wrong = data.get("wrong_answers", 0)
            attempt.technical_skipped = data.get("skipped_answers", 0)

        else:
            raise HTTPException(400, "Invalid test_type")

        # Calculate totals
        aptitude = attempt.aptitude_score or 0
        technical = attempt.technical_score or 0

        attempt.total_score = aptitude + technical

        # total questions = sum of both sections
        total_questions = data.get("total_questions", 1)

        # safer percentage calc
        if total_questions > 0:
            attempt.total_percentage = int((attempt.total_score / total_questions) * 100)

        # Mark completed only if BOTH sections submitted
        if attempt.aptitude_score is not None and attempt.technical_score is not None:
            attempt.status = "completed"
            attempt.submitted_at = datetime.utcnow()
        else:
            attempt.status = "in_progress"

        self.db.commit()
        self.db.refresh(attempt)

        return {
            "user_id": user_id,
            "test_type": test_type,
            "aptitude_score": attempt.aptitude_score,
            "technical_score": attempt.technical_score,
            "total_score": attempt.total_score,
            "percentage": attempt.total_percentage,
            "status": attempt.status
        }
    def get_user_exam_status(self, user_id: int):

        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id
        ).order_by(Attempts.attempt_id.desc()).first()

        # No attempt
        if not attempt:
            return {
                "status": "not_started",
                "message": "User has not started any test"
            }

        #In Progress
        if attempt.status == "in_progress":
            return {
                "attempt_id": attempt.attempt_id,
                "status": "in_progress",
                "aptitude_score": attempt.aptitude_score or 0,
                "technical_score": attempt.technical_score or 0,
                "message": "Test is in progress"
            }

        # Completed
        if attempt.status == "completed":
            return {
                "attempt_id": attempt.attempt_id,
                "status": "completed",
                "aptitude_score": attempt.aptitude_score or 0,
                "technical_score": attempt.technical_score or 0,
                "total_score": attempt.total_score or 0,
                "percentage": attempt.total_percentage or 0,
                "submitted_at": attempt.submitted_at
            }

    def get_exam_summary(self):

            # Subquery to get latest attempt per user
            latest_attempt_subq = (
                self.db.query(
                    Attempts.user_id,
                    func.max(Attempts.submitted_at).label("latest_submitted")
                )
                .group_by(Attempts.user_id)
                .subquery()
            )

            # Join with actual Attempts table
            latest_attempt = aliased(Attempts)

            query = (
                self.db.query(
                    ExamUsers.user_id,
                    ExamUsers.username,
                    ExamUsers.name,
                    ExamUsers.email,

                    func.coalesce(latest_attempt.aptitude_score, 0).label("aptitude_score"),
                    func.coalesce(latest_attempt.technical_score, 0).label("technical_score"),
                    func.coalesce(latest_attempt.total_score, 0).label("total_score"),
                )
                .outerjoin(
                    latest_attempt_subq,
                    latest_attempt_subq.c.user_id == ExamUsers.user_id
                )
                .outerjoin(
                    latest_attempt,
                    and_(
                        latest_attempt.user_id == latest_attempt_subq.c.user_id,
                        latest_attempt.submitted_at == latest_attempt_subq.c.latest_submitted
                    )
                )
            )

            results = query.all()

            response = []

            for row in results:
                aptitude = row.aptitude_score or 0
                technical = row.technical_score or 0
                total = row.total_score or 0

                # adjust if needed
                aptitude_total = 30
                technical_total = 20
                overall_total = 500

                response.append({
                    "user_id": row.user_id,
                    "username": row.username,
                    "name": row.name,
                    "email": row.email,

                    "aptitude_score": aptitude,
                    "aptitude_percentage": (aptitude / aptitude_total) * 100 if aptitude_total else 0,

                    "technical_score": technical,
                    "technical_percentage": (technical / technical_total) * 100 if technical_total else 0,

                    "total_score": total,
                    "total_percentage": (total / overall_total) * 100 if overall_total else 0,

                    "result": "PASS" if total > 27 else "FAIL"
                })

            return response