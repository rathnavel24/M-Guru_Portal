from datetime import datetime
from fastapi import Depends, FastAPI
from backend.app.app.api.endpoints import user
from backend.app.app.api.endpoints import Exam_assessment
from backend.app.app.api.endpoints import Exam_question
from backend.app.app.api.endpoints import Exam_option
from backend.app.app.api.endpoints import Exam_attempt
from backend.app.app.api.endpoints import Exam_answer
from backend.app.app.api.endpoints import Exam_section
from backend.app.app.api.endpoints import user, attendance
from backend.app.app.api.endpoints import task
from backend.app.app.api.endpoints import chat
from fastapi.middleware.cors import CORSMiddleware
from backend.app.app.api.endpoints import Exam_user
from backend.app.app.crud.attendance import logout_all_users
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.app.api.endpoints import feedback
from backend.app.app.api.endpoints import mentors
from backend.app.app.api.endpoints import categories
from backend.app.app.api.deps import get_db
from backend.app.app.crud.user_crud import UserServices
from backend.app.app.db.session import sessionLocal 

app = FastAPI()

origins = [
    #"https://your-frontend-url.com",
    "http://192.168.5.100:5173",
    "http://192.168.5.112:5173"

] #this is sathish bro ip ,cross  allow only this ip

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(task.router)
app.include_router(chat.router)
app.include_router(Exam_assessment.router)
app.include_router(Exam_question.router)
app.include_router(Exam_option.router)
app.include_router(Exam_attempt.router)
app.include_router(Exam_answer.router)
app.include_router(Exam_section.router)
app.include_router(attendance.router)
app.include_router(Exam_user.router)
app.include_router(feedback.router)
app.include_router(mentors.router)
app.include_router(categories.router)





import logging

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
    

    logout_all_users()
    last_global_logout_date = today
    logging.info("logout_all_users() executed at %s", now.replace(microsecond=0))


# Scheduled daily at 13:00 UTC
scheduler.add_job(safe_logout_all_users, "cron", hour=13, minute=0)

@app.on_event("startup")
def start_scheduler():
    if not scheduler.running:
     
        scheduler.start()
    logging.info("Scheduler started at %s", datetime.utcnow().replace(microsecond=0))


@app.on_event("startup")
def startup_event():
    db = sessionLocal()   
    try:
        UserServices(db, None).create_default_admin()
    finally:
        db.close()      




# @app.on_event("startup")
# async def startup_event():
#     start_scheduler(test_mode = False)