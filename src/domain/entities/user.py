"""
User domain entity

Represents a user in the system with authentication and authorization capabilities.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..value_objects.common import EntityId
from ..value_objects.email import Email
from .base import BaseEntity


class User(BaseEntity):
    """User entity with authentication and role management"""
    
    def __init__(
        self,
        id: EntityId,
        email: Email,
        username: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
        last_login: Optional[datetime] = None,
        roles: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(id, created_at, updated_at)
        self._email = email
        self._username = username
        self._password_hash = password_hash
        self._first_name = first_name
        self._last_name = last_name
        self._is_active = is_active
        self._is_verified = is_verified
        self._last_login = last_login
        self._roles = roles or []
    
    @property
    def email(self) -> Email:
        """Get user email"""
        return self._email
    
    @property
    def username(self) -> str:
        """Get username"""
        return self._username
    
    @property
    def password_hash(self) -> str:
        """Get password hash"""
        return self._password_hash
    
    @property
    def first_name(self) -> Optional[str]:
        """Get first name"""
        return self._first_name
    
    @property
    def last_name(self) -> Optional[str]:
        """Get last name"""
        return self._last_name
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        if self._first_name and self._last_name:
            return f"{self._first_name} {self._last_name}"
        elif self._first_name:
            return self._first_name
        elif self._last_name:
            return self._last_name
        else:
            return self._username
    
    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self._is_active
    
    @property
    def is_verified(self) -> bool:
        """Check if user email is verified"""
        return self._is_verified
    
    @property
    def last_login(self) -> Optional[datetime]:
        """Get last login timestamp"""
        return self._last_login
    
    @property
    def roles(self) -> List[str]:
        """Get user roles"""
        return self._roles.copy()
    
    def update_email(self, email: Email) -> None:
        """Update user email"""
        self._email = email
        self._is_verified = False  # Reset verification when email changes
        self._mark_updated()
    
    def update_username(self, username: str) -> None:
        """Update username"""
        if not username or len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        self._username = username.strip()
        self._mark_updated()
    
    def update_password_hash(self, password_hash: str) -> None:
        """Update password hash"""
        if not password_hash:
            raise ValueError("Password hash cannot be empty")
        self._password_hash = password_hash
        self._mark_updated()
    
    def update_profile(
        self, 
        first_name: Optional[str] = None, 
        last_name: Optional[str] = None
    ) -> None:
        """Update user profile information"""
        if first_name is not None:
            self._first_name = first_name.strip() if first_name else None
        if last_name is not None:
            self._last_name = last_name.strip() if last_name else None
        self._mark_updated()
    
    def activate(self) -> None:
        """Activate user account"""
        self._is_active = True
        self._mark_updated()
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self._is_active = False
        self._mark_updated()
    
    def verify_email(self) -> None:
        """Mark email as verified"""
        self._is_verified = True
        self._mark_updated()
    
    def record_login(self) -> None:
        """Record successful login"""
        self._last_login = datetime.utcnow()
        self._mark_updated()
    
    def add_role(self, role: str) -> None:
        """Add role to user"""
        if role not in self._roles:
            self._roles.append(role)
            self._mark_updated()
    
    def remove_role(self, role: str) -> None:
        """Remove role from user"""
        if role in self._roles:
            self._roles.remove(role)
            self._mark_updated()
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return role in self._roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        return any(role in self._roles for role in roles)
    
    def has_all_roles(self, roles: List[str]) -> bool:
        """Check if user has all specified roles"""
        return all(role in self._roles for role in roles)
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.has_any_role(["SUPER_ADMIN", "ADMIN"])
    
    def is_manager(self) -> bool:
        """Check if user has manager privileges"""
        return self.has_any_role(["SUPER_ADMIN", "ADMIN", "MANAGER"])
    
    def can_access_admin_panel(self) -> bool:
        """Check if user can access admin panel"""
        return self.is_active and self.is_admin()
    
    def can_manage_content(self) -> bool:
        """Check if user can manage content"""
        return self.is_active and self.is_manager()
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": str(self.id.value),
            "email": str(self.email.value),
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "roles": self.roles,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_public_dict(self) -> dict:
        """Convert user to public dictionary (without sensitive data)"""
        return {
            "id": str(self.id.value),
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __str__(self) -> str:
        return f"User(id={self.id.value}, username={self.username}, email={self.email.value})"
    
    def __repr__(self) -> str:
        return self.__str__()