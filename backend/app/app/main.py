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
from backend.app.app.api.endpoints import task
from backend.app.app.api.endpoints import chat
from fastapi.middleware.cors import CORSMiddleware
from backend.app.app.api.endpoints import Exam_user
from backend.app.app.crud.attendance import logout_all_users
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.app.api.endpoints import feedback
from backend.app.app.api.endpoints import mentors

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
   
    """
    Start the scheduler safely. 
    Do NOT automatically log out on startup to avoid wiping all tokens.
    """
    if not scheduler.running:
     
        scheduler.start()
    logging.info("Scheduler started at %s", datetime.utcnow().replace(microsecond=0))


# from backend.app.app.crud.auto_remainder import start_scheduler
# import asyncio

# @app.on_event("startup")
# async def startup_event():
#     start_scheduler(test_mode = False)



# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from backend.app.app.crud.auto_remainder import start_scheduler

# # Create a ThreadPoolExecutor
# executor = ThreadPoolExecutor()

# @app.on_event("startup")
# async def startup_event():
#     loop = asyncio.get_event_loop()
#     # Run the synchronous start_scheduler function in a separate thread
#     loop.run_in_executor(executor, start_scheduler, True)