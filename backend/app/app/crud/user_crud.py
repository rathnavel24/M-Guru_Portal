from datetime import datetime, timezone
from decimal import Decimal
from operator import and_
from unittest import result

from alembic.command import current
from backend.app.app.models.pay_email_table import Pay_email
from backend.app.app.models.portaluserfee import Fee
from backend.app.app.models.user_token import Token
from fastapi import HTTPException
from sqlalchemy import Null, or_
from datetime import date
from unittest import result
from backend.app.app.models.user_token import Token
from fastapi import HTTPException
from sqlalchemy import func, or_
from starlette import status
from backend.app.app.models.portal_users import Users
from backend.app.app.models.user_token import Token
from sqlalchemy import select, desc
from backend.app.app.models.portal_users import Users
from backend.app.app.utils import get_pagination
from sqlalchemy import select, desc, func

from backend.app.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class SignUpAbstract(ABC):

    @abstractmethod
    def user_signup():
        pass

    @abstractmethod
    def user_verification():
        pass


class SignUpDetails(SignUpAbstract):
    def __init__(self, db: Session, new_user):
        self.db = db
        self.new_user = new_user

    def user_signup(self):

        if not self.user_verification():
            raise HTTPException(status_code=409, detail="User already Exists")

        try:
            new_user = Users(
                username=self.new_user.username,
                email=self.new_user.email,
                password=get_password_hash(self.new_user.password),
                type=self.new_user.type,
                batch=self.new_user.batch,
                phone=self.new_user.phone,
                tech_stack=self.new_user.tech_stack,
            )

            self.db.add(new_user)

            # get user_id before commit
            self.db.flush()

            # create fee entry
            new_fee = Fee(
                user_id=new_user.user_id,
                total_fee=self.new_user.total_fee or 0,
                paid_amount=0,
                status=1,
                created_by="ADMIN",
            )

            self.db.add(new_fee)

            self.db.commit()

            return {"msg": "User Created Successfully", "user_id": new_user.user_id}

        except Exception as e:
            self.db.rollback()
            raise e

    def user_verification(self) -> bool:
        user = (
            self.db.query(Users)
            .filter(
                or_(
                    # Users.username == self.new_user.username,
                    Users.email
                    == self.new_user.email
                ),
                Users.status == 1,
            )
            .first()
        )

        if not user:
            return True
        else:
            return False


class LoginUser:

    def __init__(self, db, email, password):
        self.db = db
        self.email = email
        self.password = password

    def login(self, background_tasks):

        user = self.db.query(Users).filter(Users.email == self.email).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="no user found"
            )

        if not verify_password(self.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password"
            )

        token = create_access_token(data={"user_id": user.user_id, "role": user.type})

        today_token = (self.db.query(Token).filter(
                Token.user_id == user.user_id,
                func.date(Token.login) == date.today()).first())
        
        now = datetime.utcnow()
        if today_token:

            today_token.token = None
            today_token.logout=today_token.last_activity

            new_token = Token(
                token=token,
                user_id=user.user_id,
                last_activity=now,
                productive_minutes=0,
            )

        else:
            new_token = Token(
                token=token,
                user_id=user.user_id,
                last_activity=now,
                productive_minutes=0,
            )

        self.db.add(new_token)
        self.db.commit()
        return {"token": token, "token_type": "bearer", "user_type": user.type}


class UserServices:

    def __init__(self, db: Session, data):
        self.data = data
        self.db = db

    def view_user(self, batch):
        result = self.db.query(Users).filter(Users.batch == batch).all()

    def get_usersby_batch(self, batch_id):
        result = self.db.execute(
            self.db.query(
                Users.user_id,
                Users.username,
                Users.email,
                Users.batch,
                Users.phone,
                Users.tech_stack,
            )
            .filter(Users.batch == batch_id, Users.status == 1)
            .statement
        )

        return result.mappings().all()

    def soft_delete_user(self, user_id: int):
        user = (
            self.db.query(Users)
            .filter(Users.user_id == user_id, Users.status == 1)
            .first()
        )

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.status = 0
        self.db.commit()

        return {"msg": "User deleted successfully"}

    def get_all_batches(self):
        result = self.db.query(Users.batch).filter(Users.batch != None).distinct().all()
        return [r[0] for r in result]

    def get_all_users(self, page_no: int = 1, page_size: int = 10):
        """
        Fetch all active users with pagination
        """
        # total count of active users
        total_rows = (
            self.db.query(func.count(Users.user_id)).filter(Users.status == 1).scalar()
        )

        # pagination calculation
        total_pages, offset, limit = get_pagination(
            row_count=total_rows, current_page_no=page_no, default_page_size=page_size
        )

        # fetch paginated users
        users = (
            self.db.query(Users.user_id, Users.username, Users.email, Users.batch)
            .filter(Users.status == 1)
            .offset(offset)
            .limit(limit)
            .all()
        )

        # convert to dict for JSON
        users = [row._asdict() for row in users]

        return {
            "total_pages": total_pages,
            "current_page": page_no,
            "page_size": page_size,
            "total_records": total_rows,
            "data": users,
        }


class GetEmail:
    def __init__(self, db):

        self.db = db

    def get_all_emails(self, page_no: int = 1, page_size: int = 10):

        # total count
        total_rows = (
            self.db.query(func.count(Pay_email.id))
            .filter(Pay_email.status == 1)
            .scalar()
        )

        # pagination
        total_pages, offset, limit = get_pagination(
            row_count=total_rows, current_page_no=page_no, default_page_size=page_size
        )

        # fetch paginated data
        data = (
            self.db.execute(
                select(
                    Pay_email.id,
                    Pay_email.invoice_no,
                    Pay_email.amount,
                    Pay_email.is_complete,
                    Pay_email.created_at,
                    Pay_email.email_type,
                    Users.username.label("receiver_name"),
                    Users.email.label("receiver_email"),
                    Users.batch,
                )
                .where(Pay_email.status == 1)
                .order_by(desc(Pay_email.created_at))
                .offset(offset)
                .limit(limit)
            )
            .mappings()
            .all()
        )

        return {
            "total_pages": total_pages,
            "current_page": page_no,
            "page_size": page_size,
            "total_records": total_rows,
            "data": data,
        }

    def get_all_emails_bybatch(
        self, batch_id: int, page_no: int = 1, page_size: int = 10
    ):

        # total count (with batch filter)
        total_rows = (
            self.db.query(func.count(Pay_email.id))
            .join(Users, Users.user_id == Pay_email.to_id)
            .filter(Pay_email.status == 1, Users.batch == int(batch_id))
            .scalar()
        )

        # pagination
        total_pages, offset, limit = get_pagination(
            row_count=total_rows, current_page_no=page_no, default_page_size=page_size
        )

        # fetch paginated data
        data = (
            self.db.query(
                Pay_email.id,
                Pay_email.invoice_no,
                Pay_email.amount,
                Pay_email.is_complete,
                Pay_email.created_at,
                Pay_email.email_type,
                Users.username.label("receiver_name"),
                Users.email.label("receiver_email"),
                Users.batch,
            )
            .join(Users, Users.user_id == Pay_email.to_id)
            .filter(Pay_email.status == 1, Users.batch == batch_id)
            .order_by(desc(Pay_email.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        data = [row._asdict() for row in data]

        return {
            "total_pages": total_pages,
            "current_page": page_no,
            "page_size": page_size,
            "total_records": total_rows,
            "data": data,
        }


class Logout:
    def __init__(self, db):
        self.db = db

    def logout(self, current_user):
        user = current_user.get("user_id")

        # tokens = self.db.query(Token).filter(and_(Token.user_id==user,Token.logout.is_(None),Token.token.isnot(None))).first()
        tokens = (
            self.db.query(Token)
            .filter(Token.user_id == user)
            .filter(Token.logout.is_(None))
            .filter(Token.token.isnot(None))
            .first()
        )

        #now = self.db.query(func.now()).scalar()
        now=datetime.utcnow()
        tokens.logout = now
        time_diff = now - tokens.login  # timedelta

        tokens.ideal_time = Decimal(time_diff.total_seconds() / 3600).quantize(
            Decimal("0.01")
        )
        tokens.token = None
        self.db.add(tokens)
        self.db.commit()
        return {"Logout": "Successfully"}
