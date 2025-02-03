from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class BiometricData(Base):
    __tablename__ = 'biometric_data'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    fingerprint_template = Column(String(1000))  # Changed from wbf_template_id
    photo_reference = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="biometric_data") 