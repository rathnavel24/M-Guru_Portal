from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr

class UserSignUp(BaseModel):
    username : str
    email : EmailStr
    password : str 
    type : Optional[int] = 2
    
class UserLogin(BaseModel):
    email: str
    password: str


class Paymentmail(BaseModel):
    user_id:int
    amount:float
    due_date:date
    upi_id:str