from fastapi import FastAPI
from backend.app.app.api.endpoints import user


app = FastAPI()


app.include_router(user.router)