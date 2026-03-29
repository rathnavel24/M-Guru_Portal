from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr

class UserSignUp(BaseModel):
    username : str
    email : EmailStr
    password : str 
    type : Optional[int] = 2
    batch : Optional[int] = None
    
class UserLogin(BaseModel):
    email: str
    password: str


class Paymentmail(BaseModel):
    user_id:int
    amount:float
    invoice_no :str = None
    due_date:date
    note : Optional[str]=None 
    email_type : int #1=invoice ,2=remainder,3=confirmation 
    account_name: str
    account_no: str
    ifsc: str
    bank_name: str