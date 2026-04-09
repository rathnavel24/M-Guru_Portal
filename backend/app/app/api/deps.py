from datetime import datetime, timedelta
from alembic.command import current
from h11 import Data
from sqlalchemy import Null
from backend.app.app.db.session import sessionLocal
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.app.crud.user_crud import Logout
from backend.app.app.models.user_token import Token
from backend.app.app.models.portal_users import Users

from backend.app.app.crud.attendance import Check

IDLE_TIMEOUT_MINUTES = 10


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


security = HTTPBearer()

SECRET_KEY = "MqbU2rs3hlCKUWrt3ZvTeg7NxVTgTBPlJkRLWLpgoDttc8IG6I0NTzDwwzJsk"
ALGORITHM = "HS256"


def authenticate_token_value(token_value: str, db: Session):
    try:
        payload = jwt.decode(token_value, SECRET_KEY, algorithms=[ALGORITHM])

        db_token = (
            db.query(Token)
            .filter(
                Token.token == token_value,
            )
            .first()
        )

        if "role" not in payload:
            raise HTTPException(status_code=400, detail="Missing required claim: role")

        if not db_token:
            raise HTTPException(status_code=401, detail="session timeout or logged out")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(token=Depends(security), db: Session = Depends(get_db)):
    return authenticate_token_value(token.credentials, db)


def role_required(allowed_roles: list):

    def checker(user=Depends(get_current_user)):

        role = user.get("role")

        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403, detail="You are not authorized to perform this action"
            )

        return user

    return checker
