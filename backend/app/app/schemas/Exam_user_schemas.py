
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr
from typing import Optional
  

class LoginRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    name: Optional[str] = None

   

