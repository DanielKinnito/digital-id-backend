from pydantic import BaseModel, EmailStr, constr
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class UpdateField(str, Enum):
    ADDRESS = "current_address"
    PHONE = "phone_number"
    EMAIL = "email"

class UpdateRequestCreate(BaseModel):
    fields_to_update: Dict[UpdateField, str]
    reason: str

class UpdateRequestResponse(BaseModel):
    id: int
    user_id: int
    requested_changes: Dict[str, str]
    reason: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[int]
    rejection_reason: Optional[str]

    class Config:
        orm_mode = True

class ResidentIDResponse(BaseModel):
    main_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    nationality: str
    current_address: str
    phone_number: Optional[str]
    email: Optional[EmailStr]
    status: str
    institutional_ids: Dict[str, Dict[str, str]]
    photo_url: str
    created_at: datetime
    last_updated: datetime

    class Config:
        orm_mode = True 