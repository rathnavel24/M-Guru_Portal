from decimal import Decimal
from turtle import reset
from unittest import result

from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app.app.models import Token
import datetime
from backend.app.app.api.deps import get_db,sessionLocal
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def logout_all_users():
    db: Session = sessionLocal() 
    try:
        # Set logout time for all users who are logged in
        tokens = db.query(Token).filter(Token.logout.is_(None)).all()
        for token in tokens:
            token.logout = datetime.now()
            time_diff = datetime.now() - token.login  # timedelta
            token.ideal_time = Decimal(time_diff.total_seconds() / 3600).quantize(Decimal("0.01"))
            token.token=None
            db.add(token)
        db.commit()
        #print(f"[{datetime.now()}] Logout job executed. Total users logged out: {len(tokens)}")
    except Exception as e:
        print(f"Error in logout job: {e}")
    finally:
        db.close()

# Schedule the job daily at 6:30 PM
scheduler.add_job(logout_all_users, 'cron', hour=18, minute=30)
scheduler.start()


class Attendance:
    def __init__(self,db):
        self.db = db
    def attendance(self,usr_id):
        result=self.db.query(Token.login,Token.logout,Token.ideal_time).filter(Token.user_id==usr_id).all()


        return result
