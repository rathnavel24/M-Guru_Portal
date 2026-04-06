from sqlalchemy.orm import Session
from backend.app.app.crud.Code_Languages import  run_c, run_cpp, run_java, run_javascript, run_python
from backend.app.app.models import Assessments, Questions, Options, Section,Coding_Submissions,Coding_Questions


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

def evaluate_test(db: Session, answers):

    score = 0

    for ans in answers:

        correct = db.query(Options).filter_by(
            question_id=ans.question_id,
            is_correct=True
        ).first()

        if correct and correct.option_id == ans.option_id:
            score += 1

    return score

import subprocess
import tempfile
import os

def run_code(code, input_data="", language="python"):

    if isinstance(input_data, str):
        input_data = input_data.strip()

        # if "\n" not in input_data and " " in input_data:
        #     input_data = input_data.replace(" ", "\n")

    try:
        language = language.lower().strip()

        if language == "python":
            result = run_python(code, input_data)

        elif language == "javascript":
            result = run_javascript(code, input_data)

        elif language == "c":
            result = run_c(code, input_data)

        elif language == "cpp":
            result = run_cpp(code, input_data)

        elif language == "java":
            result = run_java(code, input_data)

        else:
            return {"error": "Unsupported language"}

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return {"error": stderr or "Execution Error"}

        return {"output": stdout}

    except subprocess.TimeoutExpired:
        return {"error": "Time limit exceeded"}

    except Exception as e:
        return {"error": str(e)}
    
def evaluate_code(code, test_cases, language="python"):

    def normalize(x: str):
        return " ".join(str(x).strip().lower().split())

    passed = 0
    total = len(test_cases)

    visible_results = []
    hidden_failed = 0
    outputs = []   #  ADD THIS

    for test in test_cases:

        res = run_code(code, test.input_data, language)

        is_hidden = bool(test.is_hidden)

        if res.get("error"):
            outputs.append("")   #  store empty output
            if is_hidden:
                hidden_failed += 1
            else:
                visible_results.append({
                    "status": "error",
                    "message": res["error"]
                })
            continue

        raw_output = res.get("output", "")
        outputs.append(raw_output.strip())   #  STORE OUTPUT

        output = normalize(raw_output)
        expected = normalize(test.expected_output)

        if output == expected:
            passed += 1
            status = "pass"
        else:
            status = "fail"
            if is_hidden:
                hidden_failed += 1

        if not is_hidden:
            visible_results.append({
                "status": status,
                "expected": test.expected_output,
                "got": raw_output
            })

    if passed == total:
        final_status = "PASS"
    elif passed >= 3:
        final_status = "PARTIAL_PASS"
    else:
        final_status = "FAIL"

    return {
        "passed": passed,
        "total": total,
        "visible_results": visible_results,
        "hidden_failed": hidden_failed,
        "status": final_status,
        "outputs": outputs   #  RETURN OUTPUTS
    }

def submit_code_service(db: Session, user_id: int, payload):

    question = db.query(Questions).filter(
        Questions.question_id == payload.question_id
    ).first()

    if not question:
        return {"status": "ERROR", "message": "Question not found"}

    existing = db.query(Coding_Submissions).filter(
        Coding_Submissions.user_id == user_id,
        Coding_Submissions.question_id == payload.question_id
    ).first()

    if existing:
        return {"status": "ERROR", "message": "Question already submitted"}

    test_cases = db.query(Coding_Questions).filter(
        Coding_Questions.question_id == payload.question_id
    ).all()

    result = evaluate_code(
        payload.code,
        test_cases,
        payload.language   # <-- THIS LINE FIXES EVERYTHING
    )
    submission = Coding_Submissions(
        user_id=user_id,
        question_id=payload.question_id,
        code=payload.code,
        passed=result["passed"],
        total=result["total"],
        status=result["status"],
        outputs=result["outputs"]   #  THIS IS REQUIRED
    )

    db.add(submission)
    db.commit()
    

    return {
        "question_id": payload.question_id,
        "status": result["status"],
        "passed": result["passed"],
        "total": result["total"]
    }

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

    # SUPPORT ONLY NEW FORMAT (dict)
    output_map = {}
    if submission.outputs:
        if isinstance(submission.outputs[0], dict):
            output_map = {
                o["testcase_id"]: o["output"]
                for o in submission.outputs
            }
        else:
            # fallback for old data
            for i, tc in enumerate(testcases):
                if i < len(submission.outputs):
                    output_map[tc.id] = submission.outputs[i]

    results = []
    passed_count = 0

    for tc in testcases:

        user_output = str(output_map.get(tc.id, "")).strip()
        expected_output = (tc.expected_output or "").strip()

        result = "PASS" if user_output == expected_output else "FAIL"

        if result == "PASS":
            passed_count += 1

        if not tc.is_hidden:
            results.append({
                "input": tc.input_data,
                "expected_output": expected_output,
                "user_output": user_output,
                "result": result
            })

    total = len(testcases)

    #  NEW STATUS LOGIC
    if passed_count == total and total > 0:
        final_status = "PASS"
    elif passed_count >= (total // 2):
        final_status = "PARTIAL_PASS"
    else:
        final_status = "FAIL"

    return {
        "user_id": user_id,
        "question_id": question_id,
        "status": final_status,
        "passed": passed_count,
        "total": total,
        "test_cases": results
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
evaluate_code

# -------------------------
#  RUN CODE (JUDGE0)
# -------------------------
def run_code_judge0(code, language, input_data=""):

    language = language.lower().strip()
    language_id = LANGUAGE_MAP.get(language)

    print("LANG RECEIVED:", repr(language))

    if not language_id:
        return {"error": "Unsupported language"}

    payload = {
        "language_id": language_id,
        "source_code": base64.b64encode(code.encode()).decode(),
        "stdin": base64.b64encode(input_data.encode()).decode()
    }

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(JUDGE0_URL, json=payload, headers=headers)
        result = res.json()

        def decode(x):
            if not x:
                return ""
            try:
                return base64.b64decode(x).decode("utf-8", errors="ignore")
            except Exception:
                return ""

        stdout = decode(result.get("stdout"))
        stderr = decode(result.get("stderr"))
        compile_output = decode(result.get("compile_output"))

        if stderr:
            return {"error": stderr}
        if compile_output:
            return {"error": compile_output}

        return {"output": stdout.strip()}

    except Exception as e:
        return {"error": str(e)}


# -------------------------
#  EVALUATE CODE
# -------------------------
def evaluate_code_judge0(code, test_cases, language):

    def normalize(x):
        return " ".join(str(x).strip().lower().split())

    passed = 0
    total = len(test_cases)

    outputs = []
    visible_results = []
    hidden_failed = 0

    for test in test_cases:

        res = run_code_judge0(code, language, test.input_data)

        is_hidden = bool(test.is_hidden)

        if res.get("error"):
            outputs.append("")

            if not is_hidden:
                visible_results.append({
                    "status": "error",
                    "message": res["error"]
                })
            else:
                hidden_failed += 1

            continue

        raw_output = res.get("output", "")
        outputs.append(raw_output)

        output = normalize(raw_output)
        expected = normalize(test.expected_output)

        if output == expected:
            passed += 1
            status = "pass"
        else:
            status = "fail"
            if is_hidden:
                hidden_failed += 1

        if not is_hidden:
            visible_results.append({
                "status": status,
                "expected": test.expected_output,
                "got": raw_output
            })

    final_status = (
        "PASS" if passed == total
        else "PARTIAL_PASS" if passed >= 3
        else "FAIL"
    )

    return {
        "passed": passed,
        "total": total,
        "status": final_status,
        "outputs": outputs,
        "visible_results": visible_results,
        "hidden_failed": hidden_failed
    }

def submit_code_service_judge0(db,user_id, payload, Coding_Questions, Coding_Submissions):

    solutions = payload.get("solutions", [])

    if not solutions:
        return {"status": "ERROR", "message": "No solutions provided"}

    results = []
    total_passed = 0
    total_testcases = 0

    for item in solutions:
        question_id = item.get("question_id")
        code = item.get("code")
        language = item.get("language")

        question = db.query(Questions).filter(
            Questions.question_id == question_id
        ).first()

        if not question:
            continue

        # get test cases
        test_cases = db.query(Coding_Questions).filter(
            Coding_Questions.question_id == question_id
        ).all()

        # evaluate
        result = evaluate_code_judge0(code, test_cases, language)

        # save (no duplicate check needed now OR you can keep overwrite logic)
        submission = Coding_Submissions(
            user_id=user_id,
            question_id=question_id,
            code=code,
            passed=result["passed"],
            total=result["total"],
            status=result["status"],
            outputs=result["outputs"]
        )

        db.add(submission)

        total_passed += result["passed"]
        total_testcases += result["total"]

        results.append({
            "question_id": question_id,
            "status": result["status"],
            "passed": result["passed"],
            "total": result["total"]
        })

    db.commit()

    return {
        "message": "All submissions evaluated",
        "results": results,
        "total_passed": total_passed,
        "total_testcases": total_testcases
    }