from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .role import user_roles

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    main_id = Column(String(12), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum('Male', 'Female', 'Other', name='gender_types'), nullable=False)
    nationality = Column(String(50), nullable=False, default="Ethiopian")
    current_address = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    email = Column(String(100), unique=True)
    institutional_ids = Column(JSON, default=dict)  # Store institutional IDs
    status = Column(String(20), default="active")  # active, suspended, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('auth_service.users.id'))
    last_updated_by = Column(Integer, ForeignKey('auth_service.users.id'))

    # Relationships
    biometric_data = relationship("BiometricData", back_populates="user", uselist=False)
    update_requests = relationship("UpdateRequest", back_populates="user")
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    @property
    def permissions(self):
        """Get all permissions for user's roles"""
        all_permissions = set()
        for role in self.roles:
            if role.permissions:
                all_permissions.update(role.permissions.split(','))
        return list(all_permissions) 