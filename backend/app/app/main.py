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
from fastapi.middleware.cors import CORSMiddleware
from backend.app.app.api.endpoints import Exam_user
from backend.app.app.crud.attendance import logout_all_users
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.app.api.endpoints import feedback



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
app.include_router(Exam_assessment.router)
app.include_router(Exam_question.router)
app.include_router(Exam_option.router)
app.include_router(Exam_attempt.router)
app.include_router(Exam_answer.router)
app.include_router(Exam_section.router)
app.include_router(attendance.router)
app.include_router(Exam_user.router)
app.include_router(feedback.router)







# # scheduler = BackgroundScheduler()
# #scheduler = BackgroundScheduler(timezone="UTC")


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
    #print("lin 103")
    """
    Start the scheduler safely. 
    Do NOT automatically log out on startup to avoid wiping all tokens.
    """
    if not scheduler.running:
        #print("lin 108")
        scheduler.start()
    logging.info("Scheduler started at %s", datetime.utcnow().replace(microsecond=0))


from backend.app.app.crud.auto_remainder import start_scheduler

@app.on_event("startup")
async def startup_event():
    start_scheduler(test_mode = False)

#dont change its by hari


# from datetime import datetime
# from fastapi import FastAPI
# from backend.app.app.api.endpoints import user, Exam_assessment, Exam_question, Exam_option, Exam_attempt, Exam_answer, Exam_section, attendance, Exam_user
# from fastapi.middleware.cors import CORSMiddleware
# from backend.app.app.crud.attendance import logout_all_users
# from apscheduler.schedulers.background import BackgroundScheduler
# from prometheus_client import Counter, generate_latest, start_http_server
# from fastapi.responses import Response
# import logging

# # Initialize FastAPI instance
# app = FastAPI()

# # Prometheus Metrics Setup
# REQUESTS = Counter("http_requests_total", "Total number of HTTP requests", ["method", "endpoint"])

# # Expose metrics for Prometheus
# @app.get("/metrics")
# def metrics():
#     # This is where Prometheus will scrape your metrics
#     return Response(generate_latest(), media_type="text/plain")

# # Example of tracking request count
# @app.get("/")
# async def root():
#     REQUESTS.labels(method="GET", endpoint="/").inc()
#     return {"message": "Hello World"}

# # Ensure Prometheus can scrape this metric at a specified port
# @app.on_event("startup")
# def startup():
#     # Start the Prometheus client server on port 8001 for metrics exposure
#     start_http_server(8001)

# # CORS middleware setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include the routes (endpoints)
# app.include_router(user.router)
# app.include_router(Exam_assessment.router)
# app.include_router(Exam_question.router)
# app.include_router(Exam_option.router)
# app.include_router(Exam_attempt.router)
# app.include_router(Exam_answer.router)
# app.include_router(Exam_section.router)
# app.include_router(attendance.router)
# app.include_router(Exam_user.router)

# # Initialize the scheduler for background tasks
# scheduler = BackgroundScheduler()

# # Optional: keep track of last run to prevent multiple executions
# last_global_logout_date = None

# def safe_logout_all_users():
#     global last_global_logout_date
#     now = datetime.utcnow()
#     today = now.date()
#     if last_global_logout_date == today:
#         # Already ran today, skip
#         return
#     logging.info("Logging out all users...")

#     logout_all_users()
#     last_global_logout_date = today
#     logging.info("logout_all_users() executed at %s", now.replace(microsecond=0))

# # Schedule daily logout at 13:00 UTC
# scheduler.add_job(safe_logout_all_users, "cron", hour=13, minute=0)

# @app.on_event("startup")
# def start_scheduler():
#     logging.info("Scheduler started at %s", datetime.utcnow().replace(microsecond=0))
#     if not scheduler.running:
#         scheduler.start()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)
