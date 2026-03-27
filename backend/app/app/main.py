from datetime import UTC, datetime, timezone
from fastapi import FastAPI
from backend.app.app.api.endpoints import user
from backend.app.app.api.endpoints import Exam_assessment
from backend.app.app.api.endpoints import Exam_question
from backend.app.app.api.endpoints import Exam_option
from backend.app.app.api.endpoints import Exam_attempt
from backend.app.app.api.endpoints import Exam_answer
from backend.app.app.api.endpoints import Exam_section
from backend.app.app.api.endpoints import user, attendance
from fastapi.middleware.cors import CORSMiddleware
from backend.app.app.api.endpoints import Exam_user
from backend.app.app.crud.attendance import logout_all_users
from apscheduler.schedulers.background import BackgroundScheduler


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(Exam_assessment.router)
app.include_router(Exam_question.router)
app.include_router(Exam_option.router)
app.include_router(Exam_attempt.router)
app.include_router(Exam_answer.router)
app.include_router(Exam_section.router)
app.include_router(attendance.router)
app.include_router(Exam_user.router)


scheduler = BackgroundScheduler()

'''
def run_if_missed():
    now = datetime.now()
    target_time = now.replace(hour=18, minute=30, second=0, microsecond=0)

    if now > target_time:
        logout_all_users()


@app.on_event("startup")
def start_scheduler():
    # ✅ Run missed job if server was down
    run_if_missed()

    # ✅ Schedule daily job
    scheduler.add_job(logout_all_users, "cron", hour=18, minute=30)

    if not scheduler.running:
        scheduler.start()
'''