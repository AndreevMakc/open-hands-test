"""
Role SQLAlchemy model
"""

from typing import List

from sqlalchemy import Boolean, Column, String, Text, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from .base import BaseModel
from .user_model import user_roles


class RoleModel(BaseModel):
    """Role SQLAlchemy model"""
    
    __tablename__ = "roles"
    
    # Basic role information
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Permissions stored as array of strings
    permissions = Column(ARRAY(String), default=[], nullable=False)
    
    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    users = relationship(
        "UserModel",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<RoleModel(id={self.id}, name={self.name})>"
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        permission = permission.strip().lower()
        
        # Check for wildcard permission
        if "*" in self.permissions:
            return True
        
        # Check for exact permission
        if permission in self.permissions:
            return True
        
        # Check for resource-level wildcard (e.g., "users.*")
        resource = permission.split('.')[0]
        resource_wildcard = f"{resource}.*"
        if resource_wildcard in self.permissions:
            return True
        
        return False
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if role has any of the specified permissions"""
        return any(self.has_permission(perm) for perm in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Check if role has all specified permissions"""
        return all(self.has_permission(perm) for perm in permissions)
    
    def is_admin_role(self) -> bool:
        """Check if this is an admin role"""
        return self.name in ["SUPER_ADMIN", "ADMIN"]
    
    def is_manager_role(self) -> bool:
        """Check if this is a manager role"""
        return self.name in ["SUPER_ADMIN", "ADMIN", "MANAGER"]