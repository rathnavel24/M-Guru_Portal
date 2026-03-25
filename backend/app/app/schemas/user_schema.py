from typing import Optional

from pydantic import BaseModel, EmailStr

class UserSignUp(BaseModel):
    username : str
    email : EmailStr
    password : str 
    type : Optional[str] = 'user'
    
class UserLogin(BaseModel):
    email: str
    password: str