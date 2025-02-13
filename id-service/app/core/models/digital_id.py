from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base
from enum import Enum

class IDStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

class DigitalID(Base):
    __tablename__ = "digital_ids"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    id_number = Column(String(50), unique=True, nullable=False)
    status = Column(SQLEnum(IDStatus), default=IDStatus.ACTIVE)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    issuer_id = Column(Integer, nullable=False)
    metadata = Column(String(1000))  # JSON string for additional data
    institution_id = Column(Integer, ForeignKey('institutions.id'))

    # Relationships
    history = relationship("IDHistory", back_populates="digital_id")
    institution = relationship("Institution", back_populates="digital_ids") 