
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr

  

class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfoRequest(BaseModel):
    user_id: int
    name: str
    email: EmailStr

