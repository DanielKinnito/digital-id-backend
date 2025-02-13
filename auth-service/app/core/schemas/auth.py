from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    roles: List[str]
    permissions: List[str]

class UserBase(BaseModel):
    username: str
    email: EmailStr
    institution_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    roles: List[str]

    class Config:
        from_attributes = True 