from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from app.core.models.digital_id import IDStatus

class DigitalIDBase(BaseModel):
    user_id: int
    id_number: str
    expires_at: datetime
    metadata: Optional[str] = None
    institution_id: Optional[int] = None

class DigitalIDCreate(DigitalIDBase):
    pass

class DigitalIDUpdate(BaseModel):
    status: Optional[IDStatus] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[str] = None

class IDHistoryEntry(BaseModel):
    old_status: IDStatus
    new_status: IDStatus
    changed_by: int
    reason: str
    changed_at: datetime

    class Config:
        from_attributes = True

class DigitalIDResponse(DigitalIDBase):
    id: int
    status: IDStatus
    issued_at: datetime
    issuer_id: int
    history: Optional[List[IDHistoryEntry]] = None

    class Config:
        from_attributes = True

class DigitalIDStatusUpdate(BaseModel):
    status: IDStatus
    reason: str 