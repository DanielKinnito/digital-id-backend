from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True)
    report_type = Column(String(50), nullable=False)
    data = Column(JSON, nullable=False)
    generated_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    generator = relationship("User", backref="generated_reports")
