"""
Role domain entity

Represents a role in the RBAC system with associated permissions.
"""

from datetime import datetime
from typing import List, Optional

from ..value_objects.common import EntityId
from .base import BaseEntity


class Role(BaseEntity):
    """Role entity for RBAC system"""
    
    def __init__(
        self,
        id: EntityId,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        is_active: bool = True,
        is_system: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self._name = self._validate_name(name)
        self._description = description
        self._permissions = permissions or []
        self._is_active = is_active
        self._is_system = is_system
    
    @property
    def name(self) -> str:
        """Get role name"""
        return self._name
    
    @property
    def description(self) -> Optional[str]:
        """Get role description"""
        return self._description
    
    @property
    def permissions(self) -> List[str]:
        """Get role permissions"""
        return self._permissions.copy()
    
    @property
    def is_active(self) -> bool:
        """Check if role is active"""
        return self._is_active
    
    @property
    def is_system(self) -> bool:
        """Check if role is a system role (cannot be deleted)"""
        return self._is_system
    
    def _validate_name(self, name: str) -> str:
        """Validate role name"""
        if not name or not name.strip():
            raise ValueError("Role name cannot be empty")
        
        name = name.strip().upper()
        
        if len(name) < 2:
            raise ValueError("Role name must be at least 2 characters long")
        
        if len(name) > 50:
            raise ValueError("Role name cannot exceed 50 characters")
        
        # Check for valid characters (letters, numbers, underscore)
        if not name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Role name can only contain letters, numbers, underscore and hyphen")
        
        return name
    
    def update_name(self, name: str) -> None:
        """Update role name"""
        if self._is_system:
            raise ValueError("Cannot modify system role name")
        
        self._name = self._validate_name(name)
        self._mark_updated()
    
    def update_description(self, description: Optional[str]) -> None:
        """Update role description"""
        self._description = description.strip() if description else None
        self._mark_updated()
    
    def add_permission(self, permission: str) -> None:
        """Add permission to role"""
        if not permission or not permission.strip():
            raise ValueError("Permission cannot be empty")
        
        permission = permission.strip().lower()
        
        if permission not in self._permissions:
            self._permissions.append(permission)
            self._mark_updated()
    
    def remove_permission(self, permission: str) -> None:
        """Remove permission from role"""
        if self._is_system:
            raise ValueError("Cannot modify system role permissions")
        
        permission = permission.strip().lower()
        
        if permission in self._permissions:
            self._permissions.remove(permission)
            self._mark_updated()
    
    def has_permission(self, permission: str) -> bool:
        """Check if role has specific permission"""
        permission = permission.strip().lower()
        
        # Check for wildcard permission
        if "*" in self._permissions:
            return True
        
        # Check for exact permission
        if permission in self._permissions:
            return True
        
        # Check for resource-level wildcard (e.g., "users.*")
        resource = permission.split('.')[0]
        resource_wildcard = f"{resource}.*"
        if resource_wildcard in self._permissions:
            return True
        
        return False
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if role has any of the specified permissions"""
        return any(self.has_permission(perm) for perm in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Check if role has all specified permissions"""
        return all(self.has_permission(perm) for perm in permissions)
    
    def set_permissions(self, permissions: List[str]) -> None:
        """Set role permissions (replaces existing)"""
        if self._is_system:
            raise ValueError("Cannot modify system role permissions")
        
        # Validate and normalize permissions
        normalized_permissions = []
        for perm in permissions:
            if not perm or not perm.strip():
                continue
            normalized_permissions.append(perm.strip().lower())
        
        self._permissions = normalized_permissions
        self._mark_updated()
    
    def activate(self) -> None:
        """Activate role"""
        self._is_active = True
        self._mark_updated()
    
    def deactivate(self) -> None:
        """Deactivate role"""
        if self._is_system:
            raise ValueError("Cannot deactivate system role")
        
        self._is_active = False
        self._mark_updated()
    
    def is_admin_role(self) -> bool:
        """Check if this is an admin role"""
        return self._name in ["SUPER_ADMIN", "ADMIN"]
    
    def is_manager_role(self) -> bool:
        """Check if this is a manager role"""
        return self._name in ["SUPER_ADMIN", "ADMIN", "MANAGER"]
    
    def can_manage_users(self) -> bool:
        """Check if role can manage users"""
        return self.has_any_permission([
            "users.create", "users.update", "users.delete", "users.*", "*"
        ])
    
    def can_manage_roles(self) -> bool:
        """Check if role can manage roles"""
        return self.has_any_permission([
            "roles.create", "roles.update", "roles.delete", "roles.*", "*"
        ])
    
    def can_manage_content(self) -> bool:
        """Check if role can manage content"""
        return self.has_any_permission([
            "categories.create", "categories.update", "categories.delete",
            "products.create", "products.update", "products.delete",
            "attributes.create", "attributes.update", "attributes.delete",
            "categories.*", "products.*", "attributes.*", "*"
        ])
    
    def to_dict(self) -> dict:
        """Convert role to dictionary"""
        return {
            "id": str(self.id.value),
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self) -> str:
        return f"Role(id={self.id.value}, name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()