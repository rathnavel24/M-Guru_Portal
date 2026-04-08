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

APTITUDE_PASS_MARK    = 7
TECHNICAL_PASS_MARK   = 6
PROGRAMMING_PASS_MARK = 10   # 2/4 questions = 2*5 = 10
SCHOLARSHIP_MARK      = 23

APTITUDE_TOTAL  = 15
TECHNICAL_TOTAL = 15
CODING_TOTAL    = 20   # 4 questions * 5 marks each
OVERALL_TOTAL   = 50  
 
def _build_section_statuses(aptitude_score, technical_score, programming_score):
    return (
        "PASS" if aptitude_score    >= APTITUDE_PASS_MARK    else "FAIL",
        "PASS" if technical_score   >= TECHNICAL_PASS_MARK   else "FAIL",
        "PASS" if programming_score >= PROGRAMMING_PASS_MARK else "FAIL",
    )
 
class AttemptCrud:

    def __init__(self, db: Session):
        self.db = db

    def get_user_exam_status(self, user_id: int):
            attempt = (
                self.db.query(Attempts)
                .filter(Attempts.user_id == user_id)
                .order_by(Attempts.attempt_id.desc())
                .first()
            )
    
            # ── No attempt at all ──
            if not attempt:
                return {
                    "attempt_id":      None,
                    "status":          "not_started",
                    "aptitude_score":  None,
                    "technical_score": None,
                    "coding_score":    None,
                    "message":         "User has not started any test",
                }
    
            # ── Started but no section submitted yet ──
            if attempt.status == "STARTED":
                return {
                    "attempt_id":      attempt.attempt_id,
                    "status":          "STARTED",
                    "aptitude_score":  None,
                    "technical_score": None,
                    "coding_score":    None,
                    "message":         "Test started but no section submitted yet",
                }
    
            # ── At least one section submitted ──
            if attempt.status == "in_progress":
                return {
                    "attempt_id":      attempt.attempt_id,
                    "status":          "in_progress",
                    "aptitude_score":  attempt.aptitude_score,
                    "technical_score": attempt.technical_score,
                    "coding_score":    attempt.programming_score,
                    "message":         "Test is in progress",
                }
    
            # ── Fully completed ──
            if attempt.status == "completed":
                return self.build_final_response(attempt)
    
            # ── Fallback (unknown status) ──
            return {
                "attempt_id": attempt.attempt_id,
                "status":     attempt.status,
                "message":    "Unknown status",
            }
    
    def build_final_response(self, attempt):
            
            aptitude_score    = attempt.aptitude_score    or 0
            technical_score   = attempt.technical_score   or 0
            programming_score = attempt.programming_score or 0
    
            aptitude_status, technical_status, programming_status = _build_section_statuses(
                aptitude_score, technical_score, programming_score
            )
    
            final_result = (
                "PASS"
                if aptitude_status == "PASS"
                and technical_status == "PASS"
                and programming_status == "PASS"
                else "FAIL"
            )
    
            scholarship_eligible = (attempt.total_score or 0) >= SCHOLARSHIP_MARK
    
            return {
                # ── STATUS IS NOW ALWAYS PRESENT ──
                "attempt_id": attempt.attempt_id,
                "status":     "completed",              # ← THIS WAS MISSING
    
                # Scores
                "aptitude_score":      aptitude_score,
                "aptitude_status":     aptitude_status,
                "technical_score":     technical_score,
                "technical_status":    technical_status,
                "coding_score":   programming_score,
                "programming_status":  programming_status,
    
                # Totals
                "total_score":         attempt.total_score       or 0,
                "percentage":          attempt.total_percentage  or 0,
                "final_result":        final_result,
                "scholarship_eligible": scholarship_eligible,
    
                # Aptitude breakdown
                "aptitude_correct":    attempt.aptitude_correct  or 0,
                "aptitude_wrong":      attempt.aptitude_wrong    or 0,
                "aptitude_skipped":    attempt.aptitude_skipped  or 0,
    
                # Technical breakdown
                "technical_correct":   attempt.technical_correct or 0,
                "technical_wrong":     attempt.technical_wrong   or 0,
                "technical_skipped":   attempt.technical_skipped or 0,
    
                # Coding breakdown
                "coding_correct":      attempt.coding_correct    or 0,
                "coding_wrong":        attempt.coding_wrong      or 0,
                "coding_skipped":      attempt.coding_skipped    or 0,
            }
#     def get_user_exam_status(self, user_id: int):


# #     if attempt.status == "in_progress":
# #         return {
# #             "attempt_id": attempt.attempt_id,
# #             "status": "in_progress",
# #             "aptitude_score": attempt.aptitude_score,
# #             "technical_score": attempt.technical_score,
# #             "coding_score": attempt.programming_score,
# #             "message": "Test is in progress"
# #         }
#         attempt = self.db.query(Attempts).filter(
#             Attempts.user_id == user_id
#         ).order_by(Attempts.attempt_id.desc()).first()

#         # No attempt
#         # if not attempt:
#         #     return {
#         #         "status": "not_started",
#         #         "message": "User has not started any test"
#         #     }

#         #In Progress

#         if attempt.status == "STARTED":
#             return {
#                 "attempt_id": attempt.attempt_id,
#                 "status": None,  # as you want
#                 "aptitude_score": None,
#                 "technical_score": None,
#                 "coding_score": None,
#                 "message": "Test not started"
#             }
        
#         if attempt.status == "in_progress":
#             # if attempt.aptitude_score == None and attempt.technical_score == None and attempt.programming_score == None:
#             #     progress = None
#             # else:
#             #     progress = "in_progress"
#             return {
#                 "attempt_id": attempt.attempt_id,
#                 "status": "in_progress",
#                 "aptitude_score": attempt.aptitude_score ,
#                 "technical_score": attempt.technical_score ,
#                 "coding_score": attempt.programming_score ,
#                 "message": "Test is in progress"
#             }

#         # Completed
#         # if attempt.status == "completed":
#         #     return {
#         #         "attempt_id": attempt.attempt_id,
#         #         "status": "completed",
#         #         "aptitude_score": attempt.aptitude_score or 0,
#         #         "technical_score": attempt.technical_score or 0,
#         #         "coding_score": attempt.programming_score or 0,
#         #         "total_score": attempt.total_score or 0,
#         #         "percentage": attempt.total_percentage or 0,
#         #         "submitted_at": attempt.submitted_at
#         #     }
#         if attempt.status == "completed":
#             return self.build_final_response(attempt)

    def get_exam_summary(self):

        latest_attempt_subq = (
            self.db.query(
                Attempts.user_id,
                func.max(Attempts.submitted_at).label("latest_submitted")
            )
            .group_by(Attempts.user_id)
            .subquery()
        )

        latest_attempt = aliased(Attempts)

        query = (
            self.db.query(
                ExamUsers.user_id,
                ExamUsers.username,
                ExamUsers.name,
                ExamUsers.email,
                func.coalesce(latest_attempt.aptitude_score,    0).label("aptitude_score"),
                func.coalesce(latest_attempt.technical_score,   0).label("technical_score"),
                func.coalesce(latest_attempt.programming_score, 0).label("coding_score"),
                func.coalesce(latest_attempt.total_score,       0).label("total_score"),
                func.coalesce(latest_attempt.status, "not_started").label("status"),
            )
            .outerjoin(
                latest_attempt_subq,
                latest_attempt_subq.c.user_id == ExamUsers.user_id
            )
            .outerjoin(
                latest_attempt,
                and_(
                    latest_attempt.user_id      == latest_attempt_subq.c.user_id,
                    latest_attempt.submitted_at == latest_attempt_subq.c.latest_submitted
                )
            )
        )

        results  = query.all()
        response = []

        for row in results:
            aptitude = row.aptitude_score or 0
            technical = row.technical_score or 0
            coding   = row.coding_score   or 0
            total    = row.total_score    or 0

            
            if row.status == "completed":
                aptitude_result  = "PASS" if aptitude  >= APTITUDE_PASS_MARK    else "FAIL"
                technical_result = "PASS" if technical >= TECHNICAL_PASS_MARK   else "FAIL"
                coding_result    = "PASS" if coding    >= PROGRAMMING_PASS_MARK else "FAIL"

                all_pass = (
                    aptitude_result  == "PASS" and
                    technical_result == "PASS" and
                    coding_result    == "PASS"
                )
                overall_result      = "PASS" if all_pass else "FAIL"
                scholarship_eligible = total >= SCHOLARSHIP_MARK
            else:
                aptitude_result      = None
                technical_result     = None
                coding_result        = None
                overall_result       = row.status   # "STARTED" / "in_progress" / "not_started"
                scholarship_eligible = False

            response.append({
                "user_id":  row.user_id,
                "username": row.username,
                "name":     row.name,
                "email":    row.email,

                # Scores
                "aptitude_score":       aptitude,
                "aptitude_percentage":  round((aptitude  / APTITUDE_TOTAL)  * 100, 2),
                "aptitude_result":      aptitude_result,

                "technical_score":      technical,
                "technical_percentage": round((technical / TECHNICAL_TOTAL) * 100, 2),
                "technical_result":     technical_result,

                "coding_score":         coding,
                "coding_percentage":    round((coding    / CODING_TOTAL)    * 100, 2),
                "coding_result":        coding_result,

                # Totals
                "total_score":          total,
                "total_percentage":     round((total     / OVERALL_TOTAL)   * 100, 2),

                "result":               overall_result,
                "scholarship_eligible": scholarship_eligible,
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
            Attempts.status.in_(["STARTED", "in_progress"])
        ).order_by(Attempts.attempt_id.desc()).first()

        if existing:
            return {
                "attempt_id": existing.attempt_id,
                "status": "ALREADY_STARTED"
            }

        attempt = Attempts(
            user_id=user_id,
            status="STARTED",
            started_at=datetime.utcnow(),
            aptitude_score=None,
            technical_score=None,
            programming_score=None
        )

        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)

        return {
            "attempt_id": attempt.attempt_id,
            "status": "STARTED"
        }
    
    def save_result_from_frontend(self, user_id: int, data: dict):

        attempt = self.db.query(Attempts).filter(
            Attempts.user_id == user_id,
            Attempts.status.in_(["STARTED", "in_progress"])
        ).order_by(Attempts.attempt_id.desc()).first()

        if not attempt:
            raise HTTPException(404, "No active attempt found")

        print("ATTEMPT ID:", attempt.attempt_id)  # DEBUG

        #  STORE OLD VALUES (VERY IMPORTANT)
        old_aptitude = attempt.aptitude_score
        old_technical = attempt.technical_score

        test_type = data.get("test_type")

        # ---------------- APTITUDE ----------------
        if test_type == "aptitude":

            if old_aptitude is not None:
                raise HTTPException(400, "Aptitude already submitted")

            attempt.aptitude_score = data.get("score", old_aptitude)
            attempt.aptitude_correct = data.get("correct_answers", 0)
            attempt.aptitude_wrong = data.get("wrong_answers", 0)
            attempt.aptitude_skipped = data.get("skipped_answers", 0)

            #  PRESERVE TECHNICAL
            attempt.technical_score = old_technical

        # ---------------- TECHNICAL ----------------
        elif test_type == "technical":

            if old_technical is not None:
                raise HTTPException(400, "Technical already submitted")

            attempt.technical_score = data.get("score", old_technical)
            attempt.technical_correct = data.get("correct_answers", 0)
            attempt.technical_wrong = data.get("wrong_answers", 0)
            attempt.technical_skipped = data.get("skipped_answers", 0)

            #  PRESERVE APTITUDE
            attempt.aptitude_score = old_aptitude

        else:
            raise HTTPException(400, "Invalid test_type")
        
        aptitude_score    = attempt.aptitude_score    or 0
        technical_score   = attempt.technical_score   or 0
        programming_score = attempt.programming_score or 0

        attempt.total_score = aptitude_score + technical_score + programming_score

        # Recalculate percentage
        num_coding_qs = self.db.query(Questions).filter(
            Questions.question_type == "coding"
        ).count()
        MAX_TOTAL = 15 + 15 + (num_coding_qs * 5)
        attempt.total_percentage = int(
            (attempt.total_score / MAX_TOTAL) * 100
        ) if MAX_TOTAL > 0 else 0
        
        # ---------------- STATUS ----------------
        # if attempt.aptitude_score is not None or attempt.technical_score is not None:
        #     attempt.status = "in_progress"
        # # NEW (correct):
        aptitude_done  = attempt.aptitude_score    is not None
        technical_done = attempt.technical_score   is not None
        coding_done    = attempt.programming_score is not None  # already saved if coding submitted first

        if aptitude_done and technical_done and coding_done:
            attempt.status = "completed"
        else:
            attempt.status = "in_progress"
        
        self.db.commit()
        self.db.refresh(attempt)

        return {
            "message": "Saved successfully",
            "attempt_id": attempt.attempt_id,
            "status": attempt.status,
            "aptitude_score": attempt.aptitude_score,
            "technical_score": attempt.technical_score,
            "total_score": attempt.total_score,
            "percentage": attempt.total_percentage
        }
        # ---------------- FINAL SUBMIT (CODING + TOTAL CALC) ----------------

    def submit_test(self, user_id: int):

        # ---------------- GET ALL CODING QUESTIONS ----------------
        all_questions = self.db.query(Questions).filter(
            Questions.question_type == "coding"
        ).all()

        # total_questions = len(all_questions)

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

        aptitude_status = "PASS" if aptitude_score >= 5 else "FAIL"
        technical_status = "PASS" if technical_score >= 5 else "FAIL"
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
        attempt.status = "completed"

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
    

    # def build_final_response(self, attempt):

    #     aptitude_score = attempt.aptitude_score or 0
    #     technical_score = attempt.technical_score or 0
    #     programming_score = attempt.programming_score or 0

    #     aptitude_status = "PASS" if aptitude_score >= 6 else "FAIL"
    #     technical_status = "PASS" if technical_score >= 7 else "FAIL"
    #     programming_status = "PASS" if programming_score >= 10 else "FAIL"

    #     final_result = (
    #         "PASS"
    #         if aptitude_status == "PASS"
    #         and technical_status == "PASS"
    #         and programming_status == "PASS"
    #         else "FAIL"
    #     )

    #     scholarship_eligible = attempt.total_score >= 23

    #     return {
    #         "user_id": attempt.user_id,
    #         "attempt_id": attempt.attempt_id,

    #         "aptitude_score": aptitude_score,
    #         "aptitude_status": aptitude_status,
    #         "technical_score": technical_score,
    #         "technical_status": technical_status,
    #         "programming_score": programming_score,
    #         "programming_status": programming_status,

    #         "total_score": attempt.total_score,
    #         "percentage": attempt.total_percentage,
    #         "final_result": final_result,
    #         "scholarship_eligible": scholarship_eligible,

    #         "aptitude_correct": attempt.aptitude_correct or 0,
    #         "aptitude_wrong": attempt.aptitude_wrong or 0,
    #         "aptitude_skipped": attempt.aptitude_skipped or 0,

    #         "technical_correct": attempt.technical_correct or 0,
    #         "technical_wrong": attempt.technical_wrong or 0,
    #         "technical_skipped": attempt.technical_skipped or 0,

    #         "coding_correct": attempt.coding_correct,
    #         "coding_wrong": attempt.coding_wrong,
    #         "coding_skipped": attempt.coding_skipped,
    #     }



    """
JAVASCRIPT CODE SNIPPET (FOR REFERENCE)


const lines = require("fs").readFileSync(0, "utf-8")
  .split("\n")
  .map(s => s.trim())
  .filter(Boolean);

const num = parseInt(lines[0], 10);

// Write your logic here
console.log(num);

PYTHON CODE SNIPPET (FOR REFERENCE)

import sys

input_data = sys.stdin.read().split()

num = int(input_data[0])

# import sys

# input_data = sys.stdin.read().split()
# nums = list(map(int, input_data))

# # Write your logic here
# print(nums)

# Write your logic here
print(num)

JAVA CODE SNIPPET (FOR REFERENCE)

import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StreamTokenizer st = new StreamTokenizer(br);

        st.nextToken();
        int num = (int) st.nval;

        // Write your logic here
        System.out.println(num);
    }
}

C++ CODE SNIPPET (FOR REFERENCE)

#include <iostream>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);

    int num;
    cin >> num;

    // Write your logic here
    cout << num << endl;
    return 0;
}

C CODE SNIPPET (FOR REFERENCE)

#include <stdio.h>

int main() {
    int num;
    scanf("%d", &num);

    // Write your logic here
    printf("%d\n", num);
    return 0;
}
    
    """