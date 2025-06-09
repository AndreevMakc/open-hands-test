"""
Permission checker for RBAC authorization
"""

import logging
from functools import wraps
from typing import List, Optional, Union

from fastapi import Depends, HTTPException, status

from ...domain.entities.user import User
from .auth_middleware import get_current_active_user

logger = logging.getLogger(__name__)


class PermissionChecker:
    """Service for checking user permissions"""
    
    # Predefined role permissions
    ROLE_PERMISSIONS = {
        "SUPER_ADMIN": ["*"],
        "ADMIN": [
            "users.*", "roles.*", "permissions.*",
            "categories.*", "products.*", "attributes.*",
            "cache.manage", "system.admin"
        ],
        "MANAGER": [
            "categories.create", "categories.read", "categories.update",
            "products.create", "products.read", "products.update",
            "attributes.create", "attributes.read", "attributes.update",
            "users.read"
        ],
        "USER": [
            "categories.read", "products.read", "attributes.read"
        ],
        "GUEST": [
            "categories.read", "products.read"
        ]
    }
    
    def __init__(self):
        pass
    
    def get_user_permissions(self, user: User) -> List[str]:
        """Get all permissions for a user based on their roles"""
        permissions = set()
        
        for role in user.roles:
            role_permissions = self.ROLE_PERMISSIONS.get(role, [])
            permissions.update(role_permissions)
        
        return list(permissions)
    
    def has_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has a specific permission"""
        user_permissions = self.get_user_permissions(user)
        
        # Check for wildcard permission
        if "*" in user_permissions:
            return True
        
        # Check for exact permission
        if required_permission in user_permissions:
            return True
        
        # Check for resource-level wildcard
        resource = required_permission.split('.')[0]
        resource_wildcard = f"{resource}.*"
        if resource_wildcard in user_permissions:
            return True
        
        return False
    
    def has_any_permission(self, user: User, required_permissions: List[str]) -> bool:
        """Check if user has any of the required permissions"""
        return any(self.has_permission(user, perm) for perm in required_permissions)
    
    def has_all_permissions(self, user: User, required_permissions: List[str]) -> bool:
        """Check if user has all required permissions"""
        return all(self.has_permission(user, perm) for perm in required_permissions)
    
    def has_role(self, user: User, required_role: str) -> bool:
        """Check if user has a specific role"""
        return user.has_role(required_role)
    
    def has_any_role(self, user: User, required_roles: List[str]) -> bool:
        """Check if user has any of the required roles"""
        return user.has_any_role(required_roles)
    
    def has_all_roles(self, user: User, required_roles: List[str]) -> bool:
        """Check if user has all required roles"""
        return user.has_all_roles(required_roles)
    
    def can_access_resource(
        self,
        user: User,
        resource: str,
        action: str,
        resource_owner_id: Optional[str] = None
    ) -> bool:
        """Check if user can access a specific resource with given action"""
        permission = f"{resource}.{action}"
        
        # Check basic permission
        if self.has_permission(user, permission):
            return True
        
        # Check if user is the resource owner (for user-specific resources)
        if resource_owner_id and str(user.id.value) == resource_owner_id:
            # Users can always read/update their own data
            if action in ["read", "update"]:
                return True
        
        return False
    
    def get_accessible_resources(self, user: User) -> dict:
        """Get all resources the user can access"""
        permissions = self.get_user_permissions(user)
        resources = {}
        
        for permission in permissions:
            if permission == "*":
                return {"all": ["*"]}
            
            if "." in permission:
                resource, action = permission.split(".", 1)
                if resource not in resources:
                    resources[resource] = []
                resources[resource].append(action)
        
        return resources


# Global permission checker instance
_permission_checker: Optional[PermissionChecker] = None


def get_permission_checker() -> PermissionChecker:
    """Get or create permission checker instance"""
    global _permission_checker
    
    if _permission_checker is None:
        _permission_checker = PermissionChecker()
    
    return _permission_checker


# Permission dependency functions
def require_permission(permission: str):
    """Decorator to require specific permission"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        permission_checker: PermissionChecker = Depends(get_permission_checker)
    ):
        if not permission_checker.has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    
    return dependency


def require_any_permission(permissions: List[str]):
    """Decorator to require any of the specified permissions"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        permission_checker: PermissionChecker = Depends(get_permission_checker)
    ):
        if not permission_checker.has_any_permission(current_user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(permissions)}"
            )
        return current_user
    
    return dependency


def require_all_permissions(permissions: List[str]):
    """Decorator to require all specified permissions"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        permission_checker: PermissionChecker = Depends(get_permission_checker)
    ):
        if not permission_checker.has_all_permissions(current_user, permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All these permissions required: {', '.join(permissions)}"
            )
        return current_user
    
    return dependency


def require_role(role: str):
    """Decorator to require specific role"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        permission_checker: PermissionChecker = Depends(get_permission_checker)
    ):
        if not permission_checker.has_role(current_user, role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        return current_user
    
    return dependency


def require_any_role(roles: List[str]):
    """Decorator to require any of the specified roles"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        permission_checker: PermissionChecker = Depends(get_permission_checker)
    ):
        if not permission_checker.has_any_role(current_user, roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these roles required: {', '.join(roles)}"
            )
        return current_user
    
    return dependency


def require_resource_access(resource: str, action: str, owner_field: str = None):
    """Decorator to require access to specific resource"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        permission_checker: PermissionChecker = Depends(get_permission_checker)
    ):
        # Basic permission check
        permission = f"{resource}.{action}"
        if permission_checker.has_permission(current_user, permission):
            return current_user
        
        # If no basic permission, check if user can access their own resources
        if owner_field and action in ["read", "update"]:
            # This would need additional context from the request
            # For now, just check basic permission
            pass
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to {resource}.{action}"
        )
    
    return dependency


# Convenience decorators for common permissions
def require_admin():
    """Require admin role"""
    return require_any_role(["SUPER_ADMIN", "ADMIN"])


def require_manager():
    """Require manager role or higher"""
    return require_any_role(["SUPER_ADMIN", "ADMIN", "MANAGER"])


def require_user():
    """Require any authenticated user"""
    def dependency(current_user: User = Depends(get_current_active_user)):
        return current_user
    
    return dependency