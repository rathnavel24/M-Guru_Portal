from fastapi import HTTPException
from sqlalchemy import and_, case, func, text
from sqlalchemy.orm import Session, aliased
from datetime import datetime, timedelta

from yaml import Mark
from backend.app.app import db
from backend.app.app.models.Exam_assessment import Assessments
from backend.app.app.models.Exam_attempt import Attempts
from backend.app.app.models import Answers, Options
from backend.app.app.models.Exam_questions import Questions
from backend.app.app.models.Exam_user import ExamUsers
from backend.app.app.models.Submit_coding import Coding_Submissions

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
            if attempt.aptitude_score == None and attempt.technical_score == None:
                progress = None
            else:
                progress = "in_progress"
            return {
                "attempt_id": attempt.attempt_id,
                "status": progress,
                "aptitude_score": attempt.aptitude_score ,
                "technical_score": attempt.technical_score ,
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
                    func.coalesce(latest_attempt.status,"Ongoing").label("status"),
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
                overall_total = 50

                if row.status != 'completed':
                    rslt = row.status
                else:
                    rslt = "PASS" if total >= 25 else "FAIL"

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

                    "result": rslt
                })

            return response
    def truncate_exam_users(self):
        try:
            self.db.execute(text("TRUNCATE TABLE exam_attempts RESTART IDENTITY CASCADE"))
            self.db.execute(text("TRUNCATE TABLE exam_user RESTART IDENTITY CASCADE"))
            self.db.commit()

            return {
                "message": "All data deleted successfully"
                    }

        except Exception as e:
            self.db.rollback()
            raise e
        
    #######

    # ---------------- START ----------------
    def start_attempt(self, user_id: int):

        existing = self.db.query(Attempts).filter(
            Attempts.user_id == user_id,
            Attempts.status == "STARTED"
        ).first()

        if existing:
            return {
                "attempt_id": existing.attempt_id,
                "status": "ALREADY_STARTED"
            }

        attempt = Attempts(
            user_id=user_id,
            status="STARTED",
            started_at=datetime.utcnow()
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return {
            "attempt_id": attempt.attempt_id,
            "status": "STARTED"
        }

    from datetime import datetime
    from fastapi import HTTPException

    def save_result_from_frontend(self, user_id: int, data: dict):

        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id
        ).order_by(Attempts.attempt_id.desc()).first()

        if not attempt:
            raise HTTPException(404, "No attempt found")

        test_type = data.get("test_type")

        # ---------------- APTITUDE ----------------
        if test_type == "aptitude":

            if attempt.aptitude_score is not None:
                raise HTTPException(400, "Already submitted")

            attempt.aptitude_score = data.get("score", 0)
            attempt.aptitude_correct = data.get("correct_answers", 0)
            attempt.aptitude_wrong = data.get("wrong_answers", 0)
            attempt.aptitude_skipped = data.get("skipped_answers", 0)

        # ---------------- TECHNICAL ----------------
        elif test_type == "technical":

            if attempt.technical_score is not None:
                raise HTTPException(400, "Already submitted")

            attempt.technical_score = data.get("score", 0)
            attempt.technical_correct = data.get("correct_answers", 0)
            attempt.technical_wrong = data.get("wrong_answers", 0)
            attempt.technical_skipped = data.get("skipped_answers", 0)

        else:
            raise HTTPException(400, "Invalid test_type")

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return {
            "message": "Saved successfully",
            "aptitude_score": attempt.aptitude_score,
            "technical_score": attempt.technical_score
        }

        # ---------------- FINAL SUBMIT (CODING + TOTAL CALC) ----------------
    def submit_test(self, user_id: int):

        # ---------------- GET ALL CODING QUESTIONS ----------------
        all_questions = self.db.query(Questions).filter(
            Questions.question_type == "coding"
        ).all()

        total_questions = len(all_questions)

        # ---------------- GET USER SUBMISSIONS ----------------
        coding_data = self.db.query(Coding_Submissions).filter(
            Coding_Submissions.user_id == user_id
        ).all()

        submitted_q_ids = {
            c.question_id for c in coding_data
            if c.code is not None and c.status != "SKIPPED"
        }

        submitted_count = len(submitted_q_ids)

        # ---------------- MARK SKIPPED ----------------
        for q in all_questions:
            if q.question_id not in submitted_q_ids:

                existing = next(
                    (c for c in coding_data if c.question_id == q.question_id),
                    None
                )

                if not existing:
                    skipped = Coding_Submissions(
                        user_id=user_id,
                        question_id=q.question_id,
                        code=None,
                        passed=0,
                        total=0,
                        status="SKIPPED"
                    )
                    self.db.add(skipped)

        self.db.commit()

        # ---------------- REFRESH ----------------
        coding_data = self.db.query(Coding_Submissions).filter(
            Coding_Submissions.user_id == user_id
        ).all()

        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id
        ).order_by(Attempts.attempt_id.desc()).first()

        if not attempt:
            return {"error": "Attempt not found"}

        # ---------------- CODING STATS ----------------
        attempt.coding_correct = sum(1 for c in coding_data if c.status == "PASS")
        attempt.coding_wrong = sum(1 for c in coding_data if c.status == "FAIL")
        attempt.coding_skipped = sum(1 for c in coding_data if c.status == "SKIPPED")

        # Programming score (each question = 5 marks)
        attempt.programming_score = sum(
            (5 if c.status == "PASS"
            else int((c.passed / c.total) * 5) if c.total > 0
            else 0)
            for c in coding_data
            if c.status != "SKIPPED"
        )

        # ---------------- DEFAULTS ----------------
        aptitude_score = attempt.aptitude_score or 0
        technical_score = attempt.technical_score or 0
        programming_score = attempt.programming_score or 0

        # ---------------- TOTAL SCORE ----------------
        attempt.total_score = aptitude_score + technical_score + programming_score

        # ---------------- TOTAL MAX MARKS ----------------
        # Adjust based on your system
        APTITUDE_TOTAL = 15
        TECHNICAL_TOTAL = 15
        CODING_TOTAL = 4 * 5

        MAX_TOTAL = APTITUDE_TOTAL + TECHNICAL_TOTAL + CODING_TOTAL

        # ---------------- PERCENTAGE ----------------
        attempt.total_percentage = int(
            (attempt.total_score / MAX_TOTAL) * 100
        ) if MAX_TOTAL > 0 else 0
# ---------------- SECTION PASS/FAIL (DYNAMIC) ----------------

        aptitude_status = "PASS" if aptitude_score >= 6 else "FAIL"
        technical_status = "PASS" if technical_score >= 7 else "FAIL"
        programming_status = "PASS" if programming_score >= 10 else "FAIL"
        
        scholarship_eligible = attempt.total_score >= 23 

        # ---------------- FINAL RESULT ----------------

        final_result = (
            "PASS"
            if aptitude_status == "PASS"
            and technical_status == "PASS"
            and programming_status == "PASS"
            else "FAIL"
        )

        # ---------------- FINAL STATUS ----------------
        attempt.status = "COMPLETED"

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        # ---------------- RESPONSE ----------------
        return {
            "user_id": user_id,
            "attempt_id": attempt.attempt_id,

            # Scores
            "aptitude_score": aptitude_score,
            "aptitude_status": aptitude_status,
            "technical_score": technical_score,
            "technical_status": technical_status,
            "programming_score": programming_score,
            "programming_status": programming_status,

            # Totals
            "total_score": attempt.total_score,
            "percentage": attempt.total_percentage,
            "final_result": final_result,
            "scholarship_eligible": scholarship_eligible,

            # Aptitude breakdown
            "aptitude_correct": attempt.aptitude_correct or 0,
            "aptitude_wrong": attempt.aptitude_wrong or 0,
            "aptitude_skipped": attempt.aptitude_skipped or 0,

            # Technical breakdown
            "technical_correct": attempt.technical_correct or 0,
            "technical_wrong": attempt.technical_wrong or 0,
            "technical_skipped": attempt.technical_skipped or 0,

            # Coding breakdown
            "coding_correct": attempt.coding_correct,
            "coding_wrong": attempt.coding_wrong,
            "coding_skipped": attempt.coding_skipped,
        }
    