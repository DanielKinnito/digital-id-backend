from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from enum import Enum

class Gender(str, Enum):
    MALE = 'Male'
    FEMALE = 'Female'

class UserBase(BaseModel):
    main_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    nationality: str = "Ethiopian"
    current_address: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 