from pydantic import BaseModel, EmailStr
from typing import Optional

# 🔹 LOGIN
class LoginRequest(BaseModel):
    username: str
    password: str

# 🔹 STORE name + email
class UserDetailsCreate(BaseModel):
    name: str
    email: EmailStr

# 🔹 RESPONSE
class UserResponse(BaseModel):
    user_id: int
    username: str
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True