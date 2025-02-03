from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BiometricData(Base):
    __tablename__ = 'biometric_data'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    wbf_template_id = Column(String(255), unique=True)  # Store WBF template ID
    photo_reference = Column(String(255))  # Store reference to photo location
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="biometric_data") 