from datetime import datetime, timedelta
from tabnanny import check
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

def get_current_user(token=Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        db_token = (
            db.query(Token)
            .filter(Token.token == token.credentials, Token.logout == None)
            .first())

        if not db_token:
            raise HTTPException(status_code=401, detail="Token invalid or logged out")
        
        return payload

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    


def get_current_user(token=Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        db_token = (db.query(Token).filter(Token.token == token.credentials,
                     #Token.logout == None
                     ).first())

        if not db_token:
            raise HTTPException(status_code=401, detail="Token invalid or logged out")
        
        # Track productive time
        #user_id = payload.get("user_id")  # assuming 'sub' is user id
        #user = db.query(Users).filter(Users.user_id == user_id).first()

        now = datetime.utcnow()
        if db_token.last_activity:
            diff_minutes = (now - db_token.last_activity).total_seconds() / 60
            
            if diff_minutes <= IDLE_TIMEOUT_MINUTES:
                # User is active, count time
                db_token.last_activity=now
                db_token.productive_minutes += diff_minutes
            else:
                current_user=payload
                Logout(db).logout(current_user)
                db.commit()
                raise HTTPException(status_code=401, detail="User idle, token logged out")
        db_token.last_activity = now
        db.commit()
        return payload

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(allowed_roles: list):

    def checker(user=Depends(get_current_user)):

        role = user.get("role")

        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403, detail="You are not authorized to perform this action"
            )

        return user

    return checker
