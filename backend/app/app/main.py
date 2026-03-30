from datetime import datetime
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


# scheduler = BackgroundScheduler()
#scheduler = BackgroundScheduler(timezone="UTC")


import logging

    
# def run_if_missed():
#     now = datetime.utcnow()
#     target_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
#     if now > target_time:
#         logout_all_users()
#         logging.warning("logout_all_users() called at %s", datetime.utcnow())


# @app.on_event("startup")
# def start_scheduler():
#     # Run missed logout if server started after 18:30 UTC
#     run_if_missed()

#     # Schedule daily logout at 18:30 UTC
#     scheduler.add_job(logout_all_users, "cron", hour=13, minute=0)

#     if not scheduler.running:
#         scheduler.start()


# def run_if_missed():
#     now = datetime.utcnow()
#     target_time = now.replace(hour=13, minute=0, second=0, microsecond=0)
#     if now > target_time:
#         logout_all_users()
#         logging.info("logout_all_users() executed at %s", datetime.utcnow().replace(microsecond=0))

# @app.on_event("startup")
# def start_scheduler():
#     run_if_missed()  # Handle missed logout if server started late
#     scheduler.add_job(logout_all_users, "cron", hour=13, minute=0)
#     if not scheduler.running:
#         scheduler.start()



scheduler = BackgroundScheduler()

# Optional: keep track of last run to prevent multiple executions
last_global_logout_date = None

def safe_logout_all_users():
    global last_global_logout_date
    now = datetime.utcnow()
    today = now.date()
    if last_global_logout_date == today:
        # Already ran today, skip
        return
    print("lin 93 logout all usr")

    logout_all_users()
    last_global_logout_date = today
    logging.info("logout_all_users() executed at %s", now.replace(microsecond=0))

# Scheduled daily at 13:00 UTC
scheduler.add_job(safe_logout_all_users, "cron", hour=13, minute=0)

@app.on_event("startup")
def start_scheduler():
    """
    Start the scheduler safely. 
    Do NOT automatically log out on startup to avoid wiping all tokens.
    """
    if not scheduler.running:
        scheduler.start()
    logging.info("Scheduler started at %s", datetime.utcnow().replace(microsecond=0))