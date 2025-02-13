from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SuspensionReason(str, Enum):
    LOST = "lost"
    STOLEN = "stolen"
    FRAUD = "fraud"
    OTHER = "other"

class UserSuspend(BaseModel):
    reason: SuspensionReason
    description: str
    suspension_duration_days: Optional[int] = None

class UpdateApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None

class AdminActionLog(BaseModel):
    action: str
    user_id: int
    performed_by: int
    details: dict
    timestamp: datetime

    class Config:
        orm_mode = True 