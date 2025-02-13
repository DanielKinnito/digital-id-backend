from enum import Enum
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

# Many-to-many relationship table for user roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class RoleType(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    INSTITUTIONAL_ADMIN = "INSTITUTIONAL_ADMIN"
    RESIDENT = "RESIDENT"
    STAFF = "STAFF"

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(String(1000))  # Store as comma-separated string

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles") 