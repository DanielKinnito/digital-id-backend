from pydantic import BaseModel, constr
from typing import Optional, Dict, Annotated
from datetime import datetime
from enum import Enum

ConstrainedIDNumber = constr(min_length=4, max_length=20)

class IDType(str, Enum):
    STUDENT = "student"
    EMPLOYEE = "employee"
    MEMBER = "member"
    VISITOR = "visitor"

class InstitutionalIDCreate(BaseModel):
    main_id: str
    id_type: IDType
    id_number: Annotated[str, constr(min_length=4, max_length=20)]  # Institution-specific ID number
    department: Optional[str]
    position: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    access_level: Optional[str]
    additional_info: Optional[Dict[str, str]]

class InstitutionalIDResponse(BaseModel):
    id: int
    institution_id: int
    main_id: str
    id_type: IDType
    id_number: str
    department: Optional[str]
    position: Optional[str]
    valid_from: datetime
    valid_until: Optional[datetime]
    access_level: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LimitedUserResponse(BaseModel):
    main_id: str
    first_name: str
    last_name: str
    institutional_ids: Dict[str, Dict[str, str]]
    status: str

    class Config:
        orm_mode = True 