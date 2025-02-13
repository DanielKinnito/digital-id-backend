from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class InstitutionalID(Base):
    __tablename__ = 'institutional_ids'

    id = Column(Integer, primary_key=True, index=True)
    main_id = Column(String(12), nullable=False)
    institution_id = Column(Integer, ForeignKey('institutions.id'))
    id_number = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    institution = relationship("Institution", back_populates="institutional_ids")