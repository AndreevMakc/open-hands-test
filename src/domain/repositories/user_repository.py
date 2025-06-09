"""
User repository interface

Defines the contract for user data persistence operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.user import User
from ..value_objects.email import Email


class UserRepository(ABC):
    """Abstract repository for user operations"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID"""
        pass
    
    @abstractmethod
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        role: Optional[str] = None
    ) -> List[User]:
        """List users with optional filters"""
        pass
    
    @abstractmethod
    async def count_users(
        self,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        role: Optional[str] = None
    ) -> int:
        """Count users with optional filters"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user exists by email"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        pass
    
    @abstractmethod
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with specific role"""
        pass
    
    @abstractmethod
    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name, username, or email"""
        pass