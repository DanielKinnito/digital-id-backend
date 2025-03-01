from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from app.core.models.user import UserRole

class InstitutionalAdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    institution_id: int

class AdminResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    institution_id: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    start_date: date
    end_date: date
    report_type: str

class ReportResponse(BaseModel):
    id: int
    report_type: str
    data: dict
    generated_at: datetime
    generated_by: int

    class Config:
        from_attributes = True

class InstitutionResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    institution_id: Optional[int]
    is_active: bool

    class Config:
        from_attributes = True