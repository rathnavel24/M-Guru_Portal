from datetime import datetime, timezone
from decimal import Decimal
from operator import and_
from unittest import result
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

from backend.app.app.core.security import get_password_hash, verify_password, create_access_token
from abc import ABC,abstractmethod
from sqlalchemy.orm import Session

class SignUpAbstract(ABC):

    @abstractmethod
    def user_signup():
        pass
    
    @abstractmethod
    def user_verification():
        pass

class SignUpDetails(SignUpAbstract):
    def __init__(self, db:Session, new_user):
        self.db = db
        self.new_user = new_user
    
    def user_signup(self):

        if self.user_verification():
            self.db.add(Users(
                username = self.new_user.username,
                email =  self.new_user.email,
                password = get_password_hash(self.new_user.password),
                type = self.new_user.type,
                batch = self.new_user.batch
                ))
            self.db.commit()
            return {
                "msg" : "User Created Successfully"
            }
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already Exists")

    def user_verification(self) -> bool: 
        user = self.db.query(Users).filter(
            or_(
                #Users.username == self.new_user.username,
                Users.email == self.new_user.email
            ),
            Users.status == 1
        ).first()

        if not user:
            return True
        else:
            return False
        
class LoginUser:

    def __init__(self, db, email, password):
        self.db = db
        self.email = email
        self.password = password

    def login(self,background_tasks):

        user = self.db.query(Users).filter(
            Users.email == self.email
        ).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no user found")

        if not verify_password(self.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Wrong password")


        token = create_access_token(
            data={"user_id": user.user_id,
                  "role": user.type
                })
        
        today_token = self.db.query(Token).filter(
        Token.user_id == user.user_id,
        func.date(Token.login) == date.today()   # 👈 key logic
        ).first()

        if today_token:
            
            today_token.token = token
            today_token.logout = None

        else:
            
            new_token = Token(
            token=token,
            user_id=user.user_id
            )

            self.db.add(new_token)
        self.db.commit()
        return {
            "token": token,
            "token_type": "bearer",
            "user_type" : user.type
        }
    
class UserServices:

    def __init__(self,db:Session,data):
        self.db = db
    def view_user(self,batch):
        result=self.db.query(Users).filter(Users.batch==batch).all()

class Logout:
    def __init__(self, db):
        self.db = db

    def logout(self,current_user):
        user=current_user.get("user_id")


        #tokens = self.db.query(Token).filter(and_(Token.user_id==user,Token.logout.is_(None),Token.token.isnot(None))).first()
        tokens = (
    self.db.query(Token)
    .filter(Token.user_id == user)
    .filter(Token.logout.is_(None))
    .filter(Token.token.isnot(None))
    .first()
)
        tokens.logout = datetime.utcnow()
        time_diff = datetime.utcnow() - tokens.login  # timedelta
        tokens.ideal_time = Decimal(time_diff.total_seconds() / 3600).quantize(Decimal("0.01"))
        tokens.token=None
        self.db.add(tokens)
        self.db.commit()
        return {
                "Logout" : "Successfully"
                }
        self.data = data

    def get_usersby_batch(self,batch_id):
        result = self.db.execute(
        self.db.query(
            Users.user_id,
            Users.username,
            Users.email,
            Users.batch
        )
        .filter(Users.batch == batch_id,Users.status == 1)
        .statement
    )

        return result.mappings().all()
    
    def soft_delete_user(self, user_id: int):
        user = self.db.query(Users).filter(
            Users.user_id == user_id,
            Users.status == 1
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.status = 0  
        self.db.commit()

        return {"msg": "User deleted successfully"}

