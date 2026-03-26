from fastapi import FastAPI
from backend.app.app.api.endpoints import user,attendance
from backend.app.app.api.endpoints import Exam_user


app = FastAPI()


app.include_router(user.router)
app.include_router(attendance.router)
app.include_router(Exam_user.router)
