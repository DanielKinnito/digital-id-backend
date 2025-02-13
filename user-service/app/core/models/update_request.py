from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UpdateRequestStatus(str, PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UpdateRequest(Base):
    __tablename__ = 'update_requests'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    requested_changes = Column(JSON, nullable=False)
    reason = Column(String(500), nullable=False)
    status = Column(
        String(20),
        default=UpdateRequestStatus.PENDING.value,
        nullable=False
    )
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="update_requests", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by]) 