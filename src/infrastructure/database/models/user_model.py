"""
User SQLAlchemy model
"""

from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


# Association table for user-role many-to-many relationship
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by', UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
)


class UserModel(BaseModel):
    """User SQLAlchemy model"""
    
    __tablename__ = "users"
    
    # Basic user information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roles = relationship(
        "RoleModel",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin"
    )
    
    # Self-referential relationship for assigned_by in user_roles
    assigned_roles = relationship(
        "UserModel",
        secondary=user_roles,
        primaryjoin="UserModel.id == user_roles.c.assigned_by",
        secondaryjoin="UserModel.id == user_roles.c.user_id",
        viewonly=True
    )
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email})>"
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username
    
    @property
    def role_names(self) -> List[str]:
        """Get list of role names"""
        return [role.name for role in self.roles]
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role"""
        return role_name in self.role_names
    
    def has_any_role(self, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        return any(role in self.role_names for role in role_names)
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.has_any_role(["SUPER_ADMIN", "ADMIN"])
    
    def is_manager(self) -> bool:
        """Check if user has manager privileges"""
        return self.has_any_role(["SUPER_ADMIN", "ADMIN", "MANAGER"])