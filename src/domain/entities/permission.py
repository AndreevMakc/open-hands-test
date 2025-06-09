"""
Permission domain entity

Represents a permission in the RBAC system.
"""

from datetime import datetime
from typing import Optional

from ..value_objects.common import EntityId
from .base import BaseEntity


class Permission(BaseEntity):
    """Permission entity for RBAC system"""
    
    def __init__(
        self,
        id: EntityId,
        name: str,
        description: Optional[str] = None,
        resource: str = "",
        action: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self._name = self._validate_name(name)
        self._description = description
        self._resource, self._action = self._parse_permission_name(self._name)
        
        # Override with explicit resource/action if provided
        if resource:
            self._resource = resource.strip().lower()
        if action:
            self._action = action.strip().lower()
    
    @property
    def name(self) -> str:
        """Get permission name"""
        return self._name
    
    @property
    def description(self) -> Optional[str]:
        """Get permission description"""
        return self._description
    
    @property
    def resource(self) -> str:
        """Get resource part of permission"""
        return self._resource
    
    @property
    def action(self) -> str:
        """Get action part of permission"""
        return self._action
    
    def _validate_name(self, name: str) -> str:
        """Validate permission name"""
        if not name or not name.strip():
            raise ValueError("Permission name cannot be empty")
        
        name = name.strip().lower()
        
        if len(name) < 2:
            raise ValueError("Permission name must be at least 2 characters long")
        
        if len(name) > 100:
            raise ValueError("Permission name cannot exceed 100 characters")
        
        # Check for valid format (resource.action or *)
        if name != "*" and "." not in name:
            raise ValueError("Permission name must be in format 'resource.action' or '*'")
        
        return name
    
    def _parse_permission_name(self, name: str) -> tuple[str, str]:
        """Parse permission name into resource and action"""
        if name == "*":
            return "all", "all"
        
        if "." not in name:
            return name, "all"
        
        parts = name.split(".", 1)
        resource = parts[0].strip()
        action = parts[1].strip()
        
        return resource, action
    
    def update_description(self, description: Optional[str]) -> None:
        """Update permission description"""
        self._description = description.strip() if description else None
        self._mark_updated()
    
    def is_wildcard(self) -> bool:
        """Check if this is a wildcard permission"""
        return self._name == "*"
    
    def is_resource_wildcard(self) -> bool:
        """Check if this is a resource wildcard permission (e.g., users.*)"""
        return self._action == "*" and self._resource != "all"
    
    def matches(self, required_permission: str) -> bool:
        """Check if this permission matches a required permission"""
        required_permission = required_permission.strip().lower()
        
        # Wildcard permission matches everything
        if self.is_wildcard():
            return True
        
        # Exact match
        if self._name == required_permission:
            return True
        
        # Resource wildcard match
        if self.is_resource_wildcard():
            required_resource = required_permission.split(".")[0]
            return self._resource == required_resource
        
        return False
    
    def is_admin_permission(self) -> bool:
        """Check if this is an admin-level permission"""
        admin_permissions = [
            "*",
            "system.*",
            "users.*",
            "roles.*",
            "permissions.*"
        ]
        return self._name in admin_permissions
    
    def is_content_permission(self) -> bool:
        """Check if this is a content management permission"""
        content_resources = ["categories", "products", "attributes"]
        return self._resource in content_resources
    
    def is_read_permission(self) -> bool:
        """Check if this is a read permission"""
        return self._action in ["read", "view", "get", "list"]
    
    def is_write_permission(self) -> bool:
        """Check if this is a write permission"""
        return self._action in ["create", "update", "delete", "write", "modify"]
    
    def get_permission_level(self) -> str:
        """Get permission level (admin, manager, user, guest)"""
        if self.is_wildcard() or self._name.startswith("system."):
            return "admin"
        elif self.is_admin_permission():
            return "admin"
        elif self.is_write_permission() and self.is_content_permission():
            return "manager"
        elif self.is_read_permission():
            return "user"
        else:
            return "guest"
    
    def to_dict(self) -> dict:
        """Convert permission to dictionary"""
        return {
            "id": str(self.id.value),
            "name": self.name,
            "description": self.description,
            "resource": self.resource,
            "action": self.action,
            "is_wildcard": self.is_wildcard(),
            "is_resource_wildcard": self.is_resource_wildcard(),
            "permission_level": self.get_permission_level(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __str__(self) -> str:
        return f"Permission(id={self.id.value}, name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()