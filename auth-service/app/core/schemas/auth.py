from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.models.user import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    institution_id: Optional[int]
    is_active: bool

    class Config:
        orm_mode = True 