from fastapi import HTTPException
from sqlalchemy import or_
from starlette import status
from datetime import datetime,timedelta
from backend.app.app.models.portal_users import Users
from backend.app.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.app.core.security import generate_otp , generate_otp_key
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
                type = self.new_user.type
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
            Users.status == "active"
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

        return {
            "token": token,
            "token_type": "bearer",
            "user_type" : user.type
        }