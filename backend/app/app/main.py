from fastapi import FastAPI
from backend.app.app.api.endpoints import user,attendance

app = FastAPI()


app.include_router(user.router)
app.include_router(attendance.router)