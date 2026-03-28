from decimal import Decimal
from unittest import result
from datetime import datetime
from pytz import timezone
from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.app.models import Token
from backend.app.app.api.deps import get_db, sessionLocal
from datetime import timezone
from sqlalchemy import func, cast, Date


def logout_all_users():
    db: Session = sessionLocal()
    try:
        tokens = db.query(Token).filter(Token.logout.is_(None)).all()
        # now = db.query(func.now()).scalar()

        now = datetime.utcnow()

        # Make now naive to match DB login
        if now.tzinfo:
            now_naive = now.replace(tzinfo=None)
        else:
            now_naive = now

        for token in tokens:
            token.logout = now_naive

            if token.login:
                diff = now_naive - token.login  # both naive â†’ works
                token.ideal_time = Decimal(diff.total_seconds() / 3600).quantize(
                    Decimal("0.01")
                )

            token.token = None
            db.add(token)

        db.commit()

    except Exception as e:
        return e
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
                        "first_login"
                    ),  # Earliest login of the day
                    func.max(Token.logout).label(
                        "last_logout"
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
