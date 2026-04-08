from sqlalchemy.orm import Session
from backend.app.app.crud.Code_Languages import  run_c, run_cpp, run_java, run_javascript, run_python
from backend.app.app.models import Assessments, Questions, Options, Section,Coding_Submissions,Coding_Questions
from backend.app.app.models.Exam_attempt import Attempts


def create_test(db: Session, data):

    # -------------------------
    # GET / CREATE ASSESSMENT
    # -------------------------
    assessment = db.query(Assessments).filter(
        Assessments.name == data.name
    ).first()

    if not assessment:
        assessment = Assessments(
            name=data.name,
            total_questions=len(data.questions),
            pass_mark=int(len(data.questions) * 0.6),
            total_mark=len(data.questions),
            duration_minutes=45,
            level="Easy"
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

    # -------------------------
    # LOOP QUESTIONS
    # -------------------------
    for q in data.questions:

        # -------------------------
        # GET / CREATE SECTION
        # -------------------------
        section = db.query(Section).filter_by(
            section_name=q.section
        ).first()

        if not section:
            section = Section(section_name=q.section)
            db.add(section)
            db.commit()
            db.refresh(section)

        # -------------------------
        # DETERMINE TYPE
        # -------------------------
        q_type = getattr(q, "type", "mcq")

        # -------------------------
        # INSERT QUESTION
        # -------------------------
        question = Questions(
            question_text=q.q,
            question_section=q.section,
            section_id=section.section_id,
            question_type=q_type,
            assessments_id=assessment.assessment_id
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        # -------------------------
        # MCQ LOGIC
        # -------------------------
        if q_type == "mcq":
            if not q.opts or q.ans is None:
                continue  # skip invalid MCQ safely

            options = []
            for idx, opt in enumerate(q.opts):
                options.append(
                    Options(
                        question_id=question.question_id,
                        option_label=chr(65 + idx),
                        option_text=opt,
                        is_correct=(idx == q.ans)
                    )
                )

            db.add_all(options)
            db.commit()

        # -------------------------
        # CODING LOGIC
        # -------------------------
        elif q_type == "coding":
            if not q.test_cases:
                continue  # skip invalid coding question

            for test in q.test_cases:
                tc = Coding_Questions(
                    question_id=question.question_id,
                    input_data=test.input,
                    expected_output=test.output,
                    is_hidden=getattr(test, "hidden", False)  
                )
                db.add(tc)

            db.commit()

    return {"message": "Inserted successfully"}

def get_all_questions(db: Session):

    questions = db.query(Questions).all()

    result = []

    for q in questions:
        result.append({
            "id": q.question_id,
            "question": q.question_text,
            "section": q.section.section_name if q.section else None,
            "options": [
                {
                    "id": opt.option_id,
                    "label": opt.option_label,
                    "text": opt.option_text
                }
                for opt in q.user_questions
            ]
        })

    return result


def get_tech_questions_service(db):

    questions = db.query(Questions).filter(
        Questions.question_type == "coding"
    ).all()

    result = []

    for q in questions:

        test_cases = db.query(Coding_Questions).filter(
            Coding_Questions.question_id == q.question_id
        ).all()

        result.append({
            "question_id": q.question_id,
            "question_text": q.question_text,
            "question_section": q.question_section,
            "test_cases": [
                {
                    "input": tc.input_data,
                    "output": tc.expected_output,
                    "hidden": tc.is_hidden
                }
                for tc in test_cases
            ]
        })

    return result

# def evaluate_test(db: Session, answers):

#     score = 0

#     for ans in answers:

#         correct = db.query(Options).filter_by(
#             question_id=ans.question_id,
#             is_correct=True
#         ).first()

#         if correct and correct.option_id == ans.option_id:
#             score += 1

#     return score

# import subprocess
# import tempfile
# import os

# def run_code(code, input_data="", language="python"):

#     if isinstance(input_data, str):
#         input_data = input_data.strip()

#         # if "\n" not in input_data and " " in input_data:
#         #     input_data = input_data.replace(" ", "\n")

#     try:
#         language = language.lower().strip()

#         if language == "python":
#             result = run_python(code, input_data)

#         elif language == "javascript":
#             result = run_javascript(code, input_data)

#         elif language == "c":
#             result = run_c(code, input_data)

#         elif language == "cpp":
#             result = run_cpp(code, input_data)

#         elif language == "java":
#             result = run_java(code, input_data)

#         else:
#             return {"error": "Unsupported language"}

#         stdout = result.stdout.strip()
#         stderr = result.stderr.strip()

#         if result.returncode != 0:
#             return {"error": stderr or "Execution Error"}

#         return {"output": stdout}

#     except subprocess.TimeoutExpired:
#         return {"error": "Time limit exceeded"}

#     except Exception as e:
#         return {"error": str(e)}
    
# def evaluate_code(code, test_cases, language="python"):

#     def normalize(x: str):
#         return " ".join(str(x).strip().lower().split())

#     passed = 0
#     total = len(test_cases)

#     visible_results = []
#     hidden_failed = 0
#     outputs = []   #  ADD THIS

#     for test in test_cases:

#         res = run_code(code, test.input_data, language)

#         is_hidden = bool(test.is_hidden)

#         if res.get("error"):
#             outputs.append("")   #  store empty output
#             if is_hidden:
#                 hidden_failed += 1
#             else:
#                 visible_results.append({
#                     "status": "error",
#                     "message": res["error"]
#                 })
#             continue

#         raw_output = res.get("output", "")
#         outputs.append(raw_output.strip())   #  STORE OUTPUT

#         output = normalize(raw_output)
#         expected = normalize(test.expected_output)

#         if output == expected:
#             passed += 1
#             status = "pass"
#         else:
#             status = "fail"
#             if is_hidden:
#                 hidden_failed += 1

#         if not is_hidden:
#             visible_results.append({
#                 "status": status,
#                 "expected": test.expected_output,
#                 "got": raw_output
#             })

#     if passed == total:
#         final_status = "PASS"
#     elif passed >= 3:
#         final_status = "PARTIAL_PASS"
#     else:
#         final_status = "FAIL"

#     return {
#         "passed": passed,
#         "total": total,
#         "visible_results": visible_results,
#         "hidden_failed": hidden_failed,
#         "status": final_status,
#         "outputs": outputs   #  RETURN OUTPUTS
#     }

# def submit_code_service(db: Session, user_id: int, payload):

#     question = db.query(Questions).filter(
#         Questions.question_id == payload.question_id
#     ).first()

#     if not question:
#         return {"status": "ERROR", "message": "Question not found"}

#     existing = db.query(Coding_Submissions).filter(
#         Coding_Submissions.user_id == user_id,
#         Coding_Submissions.question_id == payload.question_id
#     ).first()

#     if existing:
#         return {"status": "ERROR", "message": "Question already submitted"}

#     test_cases = db.query(Coding_Questions).filter(
#         Coding_Questions.question_id == payload.question_id
#     ).all()

#     result = evaluate_code(
#         payload.code,
#         test_cases,
#         payload.language   # <-- THIS LINE FIXES EVERYTHING
#     )
#     submission = Coding_Submissions(
#         user_id=user_id,
#         question_id=payload.question_id,
#         code=payload.code,
#         passed=result["passed"],
#         total=result["total"],
#         status=result["status"],
#         outputs=result["outputs"]   #  THIS IS REQUIRED
#     )

#     db.add(submission)
#     db.commit()
    

#     return {
#         "question_id": payload.question_id,
#         "status": result["status"],
#         "passed": result["passed"],
#         "total": result["total"]
#     }

def get_user_submissions(db, user_id: int):

    submissions = (
        db.query(Coding_Submissions)
        .filter(Coding_Submissions.user_id == user_id)
        .all()
    )

    if not submissions:
        return {
            "status": "EMPTY",
            "message": "No submissions found",
            "data": []
        }

    result = []

    for sub in submissions:

        question = db.query(Questions).filter(
            Questions.question_id == sub.question_id
        ).first()

        result.append({
            "submission_id": sub.id,
            "question_id": sub.question_id,
            "question": question.question_text if question else None,
            "code": sub.code,
            "passed": sub.passed,
            "total": sub.total,
            "status": sub.status,
            "submitted_at": sub.created_at
        })

    return {
        "status": "SUCCESS",
        "total_submissions": len(result),
        "data": result
    }


def get_coding_result(db, user_id: int, question_id: int):

    submission = db.query(Coding_Submissions).filter(
        Coding_Submissions.user_id == user_id,
        Coding_Submissions.question_id == question_id
    ).first()

    if not submission:
        return {"error": "No submission found"}

    testcases = db.query(Coding_Questions).filter(
        Coding_Questions.question_id == question_id
    ).order_by(Coding_Questions.id).all()

    # Build output map by index (since outputs is a flat list)
    output_map = {}
    if submission.outputs:
        for i, tc in enumerate(testcases):
            if i < len(submission.outputs):
                output_map[tc.id] = submission.outputs[i]

    results = []
    passed_count = 0

    for tc in testcases:
        user_output     = normalize_output(str(output_map.get(tc.id, "")))
        expected_output = normalize_output(tc.expected_output or "")

        is_pass = user_output == expected_output
        if is_pass:
            passed_count += 1

        # Show visible, hide hidden
        if not tc.is_hidden:
            results.append({
                "input":           tc.input_data,
                "expected_output": tc.expected_output,
                "user_output":     output_map.get(tc.id, ""),
                "result":          "PASS" if is_pass else "FAIL"
            })
        else:
            # Show hidden as masked
            results.append({
                "input":           "hidden",
                "expected_output": "hidden",
                "user_output":     "hidden",
                "result":          "PASS" if is_pass else "FAIL"
            })

    total = len(testcases)

    if passed_count == total and total > 0:
        final_status = "PASS"
    elif passed_count >= (total // 2):
        final_status = "PARTIAL_PASS"
    else:
        final_status = "FAIL"

    return {
        "user_id":    user_id,
        "question_id": question_id,
        "status":     final_status,
        "passed":     passed_count,
        "total":      total,
        "test_cases": results   # all 5, hidden ones masked
    }

def get_all_coding_results(db, user_id: int):

    submissions = db.query(Coding_Submissions).filter(
        Coding_Submissions.user_id == user_id
    ).all()

    final_result = []

    for sub in submissions:

        #  FIX: USE Coding_Questions
        testcases = db.query(Coding_Questions).filter(
            Coding_Questions.question_id == sub.question_id
        ).order_by(Coding_Questions.id).all()

        passed_count = 0

        for i, tc in enumerate(testcases):

            user_output = ""
            if sub.outputs and i < len(sub.outputs):
                user_output = str(sub.outputs[i]).strip()

            expected_output = (tc.expected_output or "").strip()

            if user_output == expected_output:
                passed_count += 1

        total = len(testcases)

        final_result.append({
            "question_id": sub.question_id,
            "status": "PASS" if passed_count == total and total > 0 else "FAIL",
            "passed": passed_count,
            "total": total
        })

    return {
        "user_id": user_id,
        "questions": final_result
    }


####################

import requests
import base64

JUDGE0_URL = "https://ce.judge0.com/submissions?wait=true&base64_encoded=true"


LANGUAGE_MAP = {
    "python": 71,
    "javascript": 63,
    "cpp": 54,
    "c": 50,
    "java": 62
}
# evaluate_code

# # -------------------------
# #  RUN CODE (JUDGE0)
# # -------------------------
# def run_code_judge0(code, language, input_data=""):

#     language = language.lower().strip()
#     language_id = LANGUAGE_MAP.get(language)

#     print("LANG RECEIVED:", repr(language))

#     if not language_id:
#         return {"error": "Unsupported language"}

#     payload = {
#         "language_id": language_id,
#         "source_code": base64.b64encode(code.encode()).decode(),
#         "stdin": base64.b64encode(input_data.encode()).decode()
#     }

#     headers = {"Content-Type": "application/json"}

#     try:
#         res = requests.post(JUDGE0_URL, json=payload, headers=headers)
#         result = res.json()

#         def decode(x):
#             if not x:
#                 return ""
#             try:
#                 return base64.b64decode(x).decode("utf-8", errors="ignore")
#             except Exception:
#                 return ""

#         stdout = decode(result.get("stdout"))
#         stderr = decode(result.get("stderr"))
#         compile_output = decode(result.get("compile_output"))

#         if stderr:
#             return {"error": stderr}
#         if compile_output:
#             return {"error": compile_output}

#         return {"output": stdout.strip()}

#     except Exception as e:
#         return {"error": str(e)}




# ─────────────────────────────────────────────
#  UNIFIED NORMALIZER  (all 5 languages)
# ─────────────────────────────────────────────
def normalize_output(raw: str) -> str:
    if not raw:
        return ""
    # Strip each line, remove blanks, lowercase — but DON'T join with \n
    lines = [line.strip().lower() for line in raw.strip().splitlines()]
    lines = [l for l in lines if l]
    return " ".join(lines) 
 
 
# ─────────────────────────────────────────────
#  RUN CODE  (Judge0)
# ─────────────────────────────────────────────
def run_code_judge0(code: str, language: str, input_data: str = "") -> dict:
    language = language.lower().strip()
    language_id = LANGUAGE_MAP.get(language)
 
    #print("LANG RECEIVED:", repr(language))
 
    if not language_id:
        return {"error": f"Unsupported language: {language}"}
 
    payload = {
        "language_id": language_id,
        "source_code": base64.b64encode(code.encode()).decode(),
        "stdin":       base64.b64encode((input_data or "").encode()).decode(),
    }
 
    try:
        res    = requests.post(JUDGE0_URL, json=payload,
                               headers={"Content-Type": "application/json"},
                               timeout=15)
        result = res.json()
 
        def decode(x):
            if not x:
                return ""
            try:
                return base64.b64decode(x).decode("utf-8", errors="ignore")
            except Exception:
                return ""
 
        stdout         = decode(result.get("stdout"))
        stderr         = decode(result.get("stderr"))
        compile_output = decode(result.get("compile_output"))
 
        if compile_output and compile_output.strip():
            return {"error": compile_output.strip()}
        if stderr and stderr.strip():
            return {"error": stderr.strip()}
 
        # Normalize right here so every caller gets clean output
        return {"output": normalize_output(stdout)}
 
    except requests.Timeout:
        return {"error": "Time limit exceeded"}
    except Exception as e:
        return {"error": str(e)}
 
# ─────────────────────────────────────────────
#  EVALUATE CODE  (Judge0)
# ─────────────────────────────────────────────
def evaluate_code_judge0(code: str, test_cases, language: str) -> dict:
 
    passed          = 0
    total           = len(test_cases)
    outputs         = []        # flat string per test case
    visible_results = []
    hidden_failed   = 0
 
    for test in test_cases:
        res       = run_code_judge0(code, language, test.input_data)
        is_hidden = bool(test.is_hidden)
 
        if res.get("error"):
            outputs.append("")          # empty slot keeps index alignment
            if is_hidden:
                hidden_failed += 1
            else:
                visible_results.append({
                    "status":  "error",
                    "message": res["error"],
                })
            continue
 
        # output already normalized by run_code_judge0
        # got_output      = res.get("output", "")
        # expected_output = normalize_output(test.expected_output)
 
        # outputs.append(got_output)      # flat string

        raw_output = res.get("output", "")

        outputs.append(raw_output)   # store raw (no \n artifacts)

    # Compare using normalize
        if normalize_output(raw_output) == normalize_output(test.expected_output):
#     passed += 1
        # if got_output == expected_output:
            passed += 1
            status = "pass"
        else:
            status = "fail"
            if is_hidden:
                hidden_failed += 1
 
        if not is_hidden:
            visible_results.append({
                "status":   status,
                "expected": test.expected_output,
                "got":      raw_output,
            })
 
    # Status thresholds
    half = total // 2 if total > 0 else 0
    if passed == total and total > 0:
        final_status = "PASS"
    elif passed > half:
        final_status = "PARTIAL_PASS"
    else:
        final_status = "FAIL"
 
    return {
        "passed":          passed,
        "total":           total,
        "status":          final_status,
        "outputs":         outputs,         # list of flat strings
        "visible_results": visible_results,
        "hidden_failed":   hidden_failed,
    }
 
def submit_code_service_judge0(db: Session, user_id: int, payload: dict) -> dict:

    solutions = payload.get("solutions", [])
    
    if not solutions:
        return {"status": "ERROR", "message": "No solutions provided"}

    results       = []
    submitted_ids = set()

    # ── evaluate & save each submitted question ──
    for item in solutions:
        question_id = item.get("question_id")
        code        = item.get("code", "")
        language    = item.get("language", "python")
        submitted_ids.add(question_id)

        test_cases = db.query(Coding_Questions).filter(
            Coding_Questions.question_id == question_id
        ).all()

        result = evaluate_code_judge0(code, test_cases, language)
        

        # Delete any previous submission for this question
        db.query(Coding_Submissions).filter(
            Coding_Submissions.user_id     == user_id,
            Coding_Submissions.question_id == question_id,
        ).delete()

        db.add(Coding_Submissions(
            user_id     = user_id,
            question_id = question_id,
            code        = code,
            passed      = result["passed"],
            total       = result["total"],
            status      = result["status"],
            outputs     = result["outputs"],
        ))

        results.append({
            "question_id": question_id,
            "status":      result["status"],
            "passed":      result["passed"],
            "total":       result["total"],
        })

    db.commit()

    # ── mark skipped questions ──
    all_coding_qs = db.query(Questions).filter(
        Questions.question_type == "coding"
    ).all()

    for q in all_coding_qs:
        if q.question_id not in submitted_ids:
            existing = db.query(Coding_Submissions).filter(
                Coding_Submissions.user_id     == user_id,
                Coding_Submissions.question_id == q.question_id,
            ).first()
            if not existing:
                db.add(Coding_Submissions(
                    user_id     = user_id,
                    question_id = q.question_id,
                    code        = None,
                    passed      = 0,
                    total       = 0,
                    status      = "SKIPPED",
                    outputs     = [],
                ))

    db.commit()

    # ── calculate coding score ──
    all_subs = db.query(Coding_Submissions).filter(
        Coding_Submissions.user_id == user_id
    ).all()

    coding_correct  = sum(1 for c in all_subs if c.status == "PASS")
    coding_wrong    = sum(1 for c in all_subs if c.status in ("FAIL", "PARTIAL_PASS"))
    coding_skipped  = sum(1 for c in all_subs if c.status == "SKIPPED")

    programming_score = sum(
        (5 if c.status == "PASS"
         else int((c.passed / c.total) * 5) if c.total > 0
         else 0)
        for c in all_subs
        if c.status != "SKIPPED"
    )

    # ── fetch active attempt ──
    attempt = db.query(Attempts).filter(
        Attempts.user_id == user_id,
        Attempts.status.in_(["STARTED", "in_progress"]),
    ).order_by(Attempts.attempt_id.desc()).first()

    if not attempt:
        return {"status": "ERROR", "message": "No active attempt found"}

    # ── read aptitude & technical from attempt ──
    aptitude_score  = attempt.aptitude_score  or 0
    technical_score = attempt.technical_score or 0

    # ── calculate totals using local variables ──
    total_score = aptitude_score + technical_score + programming_score

    num_coding_qs   = db.query(Questions).filter(Questions.question_type == "coding").count()
    MAX_PROGRAMMING = num_coding_qs * 5
    MAX_TOTAL       = 15 + 15 + MAX_PROGRAMMING
    percentage      = int((total_score / MAX_TOTAL) * 100) if MAX_TOTAL > 0 else 0

    # ── update attempt ──
    attempt.programming_score = programming_score
    attempt.coding_correct    = coding_correct
    attempt.coding_wrong      = coding_wrong
    attempt.coding_skipped    = coding_skipped
    attempt.total_score       = total_score
    attempt.total_percentage  = percentage

    db.flush()  # flush so session reflects all changes before status check

    # ── mark completed only if ALL 3 sections done ──
    aptitude_done  = attempt.aptitude_score    is not None
    technical_done = attempt.technical_score   is not None
    coding_done    = attempt.programming_score is not None

    if aptitude_done and technical_done and coding_done:
        attempt.status = "completed"
    else:
        attempt.status = "in_progress"

    db.commit()
    db.refresh(attempt)

    return {
        "status":            attempt.status,
        "aptitude_score":    aptitude_score,
        "technical_score":   technical_score,
        "programming_score": programming_score,
        "coding_correct":    coding_correct,
        "coding_wrong":      coding_wrong,
        # "coding_skipped":    coding_skipped,
        "total_score":       total_score,
        "percentage":        percentage,
        "results":           results,
    }
