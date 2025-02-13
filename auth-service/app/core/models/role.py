from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(String(1000))  # Store as comma-separated string
    is_system_role = Column(Boolean, default=False)  # To identify built-in roles
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def add_permission(self, permission: str):
        """Add a permission to the role"""
        current_permissions = set(self.permissions.split(',') if self.permissions else [])
        current_permissions.add(permission)
        self.permissions = ','.join(sorted(current_permissions))

    def remove_permission(self, permission: str):
        """Remove a permission from the role"""
        if not self.permissions:
            return
        current_permissions = set(self.permissions.split(','))
        current_permissions.discard(permission)
        self.permissions = ','.join(sorted(current_permissions)) 