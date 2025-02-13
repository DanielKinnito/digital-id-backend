from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import Base
from .digital_id import IDStatus

class IDHistory(Base):
    __tablename__ = "id_history"

    id = Column(Integer, primary_key=True, index=True)
    digital_id_id = Column(Integer, ForeignKey('digital_ids.id'))
    old_status = Column(SQLEnum(IDStatus))
    new_status = Column(SQLEnum(IDStatus))
    changed_by = Column(Integer, nullable=False)  # User ID who made the change
    reason = Column(String(500))
    changed_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    digital_id = relationship("DigitalID", back_populates="history") 