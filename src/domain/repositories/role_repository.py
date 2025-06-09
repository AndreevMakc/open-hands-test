"""
Role repository interface

Defines the contract for role data persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.role import Role


class RoleRepository(ABC):
    """Abstract repository for role operations"""
    
    @abstractmethod
    async def create(self, role: Role) -> Role:
        """Create a new role"""
        pass
    
    @abstractmethod
    async def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Get role by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        pass
    
    @abstractmethod
    async def update(self, role: Role) -> Role:
        """Update existing role"""
        pass
    
    @abstractmethod
    async def delete(self, role_id: UUID) -> bool:
        """Delete role by ID"""
        pass
    
    @abstractmethod
    async def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> List[Role]:
        """List roles with optional filters"""
        pass
    
    @abstractmethod
    async def count_roles(
        self,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None
    ) -> int:
        """Count roles with optional filters"""
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str) -> bool:
        """Check if role exists by name"""
        pass
    
    @abstractmethod
    async def get_roles_with_permission(self, permission: str) -> List[Role]:
        """Get all roles that have specific permission"""
        pass
    
    @abstractmethod
    async def get_system_roles(self) -> List[Role]:
        """Get all system roles"""
        pass
    
    @abstractmethod
    async def search_roles(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Role]:
        """Search roles by name or description"""
        pass