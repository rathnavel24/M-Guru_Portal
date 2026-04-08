from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr

class UserSignUp(BaseModel):
    username : str
    email : EmailStr
    password : str 
    type : Optional[int] = 2
    batch : Optional[int] = None
    monthly_installment : Optional[bool]=True
    emi_amount : Optional[float]
    total_fee: Optional[float] = 0
    phone: Optional[str]
    tech_stack: str  
    
class UserLogin(BaseModel):
    email: str
    password: str


class Paymentmail(BaseModel):
    user_id:int
    amount:float
    invoice_no :Optional[str] = None
    due_date:Optional[date] = None
    note : Optional[str]=None 
    email_type : int #1=invoice ,2=remainder,3=confirmation 
    reference_no :Optional[str] = None
    account_name: str
    account_no: str
    ifsc: str
    bank_name: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password : Optional[str] = None
    user_type : Optional[int] = 2
    batch: Optional[int] = None
    tech_stack: Optional[str] = None
    total_fee: Optional[float] = None
    paid_amount: Optional[float] = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class AdminResetPassword(BaseModel):
    user_id: int
    new_password: str