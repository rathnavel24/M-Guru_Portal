from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.app.models import Token
from backend.app.app.api.deps import sessionLocal
from sqlalchemy import func, cast, Date
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

def logout_all_users():
    db: Session = sessionLocal()
    try:
        tokens = db.query(Token).filter(Token.logout.is_(None)).all()
        print("its from logout_all_users ")

        now = datetime.utcnow()

        for token in tokens:
            token.logout = now

            # if token.login:
            #     diff = now - token.login
            #     token.ideal_time = Decimal(diff.total_seconds() / 3600).quantize(
            #         Decimal("0.01")
            #     )

            token.token = None
            db.add(token)
            print("all user token deleted")
        db.commit()

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


class Attendance:
    def __init__(self, db):
        self.db = db

    def attendance(self, usr_id):
        try:
            result = (
                self.db.query(
                    cast(Token.login, Date).label("date"),  # Extract day from login
                    func.min(Token.login).label(
                        "check-in"
                    ),  # Earliest login of the day
                    func.max(Token.logout).label(
                        "check-out"
                    ),  # Latest logout of the day
                    func.sum(Token.productive_minutes).label(
                        "productive_minutes"
                    ),  # Sum of productive minutes
                )
                .filter(Token.user_id == usr_id)  # Filter for a single user
                .group_by(cast(Token.login, Date))  # Group by day
                .order_by(cast(Token.login, Date))  # Optional: order by date
                .all())

            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            return [row._asdict() for row in result]
        except Exception as e:
            return e
        
class Check:
    def __init__(self, db):
        self.db = db
    
    def checkin(self,current_user):
        user_id=current_user.get("user_id")
        result=self.db.query(Token).filter(Token.user_id==user_id,Token.token!=None,).first()
        result.login=datetime.utcnow()
        self.db.commit()
        return None
    
    def checkout(self,current_user):
        user_id=current_user.get("user_id")
        user_id=current_user.get("user_id")
        result=self.db.query(Token).filter(Token.user_id==user_id,Token.token!=None,).first()
        result.logout=datetime.utcnow()
        self.db.commit()
        return None
