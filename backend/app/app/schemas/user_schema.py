from typing import Optional

from pydantic import BaseModel, EmailStr

class UserSignUp(BaseModel):
    username : str
    email : EmailStr
    password : str 
    type : Optional[int] = 2
    
class UserLogin(BaseModel):
    email: str
    password: str