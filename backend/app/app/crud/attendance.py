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


def logout_all_users():
    db: Session = sessionLocal()
    try:
        tokens = db.query(Token).filter(Token.logout.is_(None)).all()
        now = db.query(func.now()).scalar()

        # Make now naive to match DB login
        if now.tzinfo:
            now_naive = now.replace(tzinfo=None)
        else:
            now_naive = now

        for token in tokens:
            token.logout = now_naive

            if token.login:
                diff = now_naive - token.login  # both naive â†’ works
                token.ideal_time = Decimal(diff.total_seconds() / 3600).quantize(Decimal("0.01"))

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
                self.db.query(Token.login, Token.logout, Token.ideal_time)
                .filter(Token.user_id == usr_id)
                .all()
            )

            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            return [row._asdict() for row in result]
        except Exception as e:
            return e
