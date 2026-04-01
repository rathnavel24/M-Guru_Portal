from decimal import Decimal
from datetime import date, datetime
from fastapi import HTTPException
from sqlalchemy import Null, asc, desc, func
from sqlalchemy.orm import Session
from backend.app.app.models import Token
from backend.app.app.api.deps import sessionLocal
from sqlalchemy import func, cast, Date
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

now = datetime.utcnow()
IDLE_TIMEOUT_MINUTES = 1


def logout_all_users():
    db: Session = sessionLocal()
    try:
        tokens = db.query(Token).filter(Token.logout.is_(None)).all()
        # print("its from logout_all_users ")

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
            # print("all user token deleted")
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
                        "check_in"
                    ),  # Earliest login of the day
                    func.max(Token.logout).label(
                        "check_out"
                    ),  # Latest logout of the day
                    func.sum(Token.productive_minutes).label(
                        "productive_minutes"
                    ),  # Sum of productive minutes
                )
                .filter(Token.user_id == usr_id)  # Filter for a single user
                .group_by(cast(Token.login, Date))  # Group by day
                .order_by(cast(Token.login, Date))  # Optional: order by date
                .all()
            )

            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            return [row._asdict() for row in result]
        except Exception as e:
            return e


class Check:
    def __init__(self, db):
        self.db = db

    def checkinnn(self, current_user):
        user_id = current_user.get("user_id")
        result = (
            self.db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.token != None,
                func.date(Token.login) == date.today(),
            )
            .first()
        )

        if result:
            if not result.logout:
                result.logout = now
                tok = Token(
                    Token.token == result.token,
                    Token.last_activity == result.last_activity,
                    Token.productive_minutes == result.productive_minutes,
                )
                self.db.add(tok)
                self.db.commit()
                result.token = None

            tok = Token(
                Token.token == result.token,
                Token.last_activity == result.last_activity,
                Token.productive_minutes == result.productive_minutes,
            )
            self.db.add(tok)
            self.db.commit()

        # tok = Token(
        #     Token.token == result.token,
        #     Token.last_activity == result.last_activity,
        #     Token.productive_minutes == result.productive_minutes,)
        # self.db.add(tok)
        # self.db.commit()

        # result.login = now
        # result.last_activity = now
        # self.db.commit()

        return "checked in"

    def checkin(self, current_user):
        user_id = current_user.get("user_id")
        now = datetime.utcnow()  # Define current time

        # First query: check for an active session with token not None, and today's login date
        resultt = (
            self.db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.token.isnot(None),
                func.date(Token.login) == date.today(),
            )  # .order_by(desc(Token.logout))
            .first()
        )
        result = (
            self.db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.token.isnot(None),  # Ensure that token is not None
                # func.date(Token.login) == date.today()
            )
            .order_by(desc(Token.logout))  # Order by most recent logout time
            .first()
        )  # Retrieve only the most recent entry

        if result:
            # If there's no logout (user already logged in), set logout time and create new token record
            if not result.logout:
                result.logout = now  # Mark logout time
                self.db.commit()

                tok = Token(  # Create new Token record
                    user_id=user_id,
                    token=result.token,  # Retain the same token or generate a new one if needed
                    last_activity=now,
                    productive_minutes=0,
                    login=now,
                )
                self.db.add(tok)  # Add the new Token to the database
                self.db.commit()

                result.token = None  # Clear the old token
                result.last_activity = None
                # result.productive_minutes=None
                self.db.commit()

                return "checked_in"

            # If user is already logged out, create a new Token entry
            else:
                # print("added")
                tok = Token(
                    user_id=user_id,
                    token=result.token,  # You might want to generate a new token here
                    last_activity=now,
                    productive_minutes=0,
                    login=now,
                )
                self.db.add(tok)
                self.db.commit()
                return "checked_in_again"  # More descriptive response when user was already logged out

        # If no result found in the first query, attempt to get any token for this user
        result = self.db.query(Token).filter(Token.user_id == user_id).first()
        if result:
            result.login = now
            result.last_activity = now
            result.productive_minutes = 0  # Reset productive minutes

            # Commit the updated result if it's a new session or recheck
            self.db.commit()
            return "new_session_created"

        return "no_active_session"  # If no token is found at all

    def checkout(self, user_id):

        # user_id=current_user.get("user_id")
        result = (
            self.db.query(Token)
            .filter(Token.user_id == user_id, Token.token != None, Token.logout == None)
            .first()
        )

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        result.logout = datetime.utcnow()
        # result.last_activity = now

        self.db.commit()
        return "checked out"

    def etatusss(self, current_user):
        user_id = current_user.get("user_id")

        results = (
            self.db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.token != None,
            )
            .first()
        )

        # print(results.last_activity)

        if current_user.get("role") == 2:
            if results.last_activity:
                diff_minutes = (now - results.last_activity).total_seconds() / 60
                # diff_minutes = round(diff_minutess, 2)

                if diff_minutes <= IDLE_TIMEOUT_MINUTES:

                    results.last_activity = now
                    # db_token.productive_minutes += diff_minutes

                    results.productive_minutes = (
                        results.productive_minutes or 0
                    ) + diff_minutes

                    self.db.commit()
                    return "time_added"

                results.logout = now

                # db_token.token=None
                self.db.commit()
                # user_id=result.user_id
                # Check(db).checkout(user_id)
                # print("User Idle, logged out")
                # raise HTTPException(status_code=401, detail="User Idle, logged out")
                self.checkout()
                return "time_out"

    def statuss(self, current_user):
        user_id = current_user.get("user_id")

        now = datetime.utcnow()  # ✅ define current time

        results = (
            self.db.query(Token)
            .filter(
                Token.user_id == user_id,
                Token.token.isnot(None),  # ✅ better syntax
            )
            .order_by(desc(Token.token_id))
            .first()
        )

        # ✅ check if token exists
        if not results:
            return "no_active_session"

        # ✅ only for role 2 users
        if current_user.get("role") == 2:

            if results.last_activity:
                # print(results.token_id,now)
                diff_minutes = (now - results.last_activity).total_seconds() / 60

                if diff_minutes <= IDLE_TIMEOUT_MINUTES:
                    results.last_activity = now
                    results.productive_minutes = (
                        results.productive_minutes or 0
                    ) + diff_minutes

                    self.db.commit()
                    return "time_added"

                # ⏱️ user idle timeout
                results.logout = now
                self.db.commit()

                return "time_out"

            # ✅ handle first-time activity
            else:
                results.last_activity = now
                self.db.commit()
                return "initialized"
        results.last_activity = now
        results.productive_minutes = (
                        results.productive_minutes or 0
                    ) + diff_minutes

        self.db.commit()
        return "time_added"
