"""
Authentication middleware for FastAPI
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ..database.repositories import get_user_repository
from ..database.connection import get_db_session
from .jwt_service import get_jwt_service

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


class AuthenticationMiddleware:
    """Authentication middleware for JWT tokens"""
    
    def __init__(self):
        self.jwt_service = get_jwt_service()
    
    async def get_current_user_optional(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        session: AsyncSession = Depends(get_db_session)
    ) -> Optional[User]:
        """Get current user from token (optional - returns None if no token)"""
        if not credentials:
            return None
        
        user_repository = get_user_repository(session)
        return await self._authenticate_user(credentials.credentials, user_repository)
    
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db_session)
    ) -> User:
        """Get current user from token (required - raises exception if no token)"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_repository = get_user_repository(session)
        user = await self._authenticate_user(credentials.credentials, user_repository)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    async def get_current_active_user(
        self,
        current_user: User = Depends(lambda: AuthenticationMiddleware().get_current_user)
    ) -> User:
        """Get current active user (must be active)"""
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        return current_user
    
    async def get_current_verified_user(
        self,
        current_user: User = Depends(lambda: AuthenticationMiddleware().get_current_active_user)
    ) -> User:
        """Get current verified user (must be active and verified)"""
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
        
        return current_user
    
    async def _authenticate_user(
        self,
        token: str,
        user_repository: UserRepository
    ) -> Optional[User]:
        """Authenticate user from JWT token"""
        try:
            # Verify token
            payload = self.jwt_service.verify_access_token(token)
            
            if not payload:
                logger.warning("Invalid or expired token")
                return None
            
            # Extract user ID
            user_id_str = payload.get("sub")
            if not user_id_str:
                logger.warning("Token missing user ID")
                return None
            
            try:
                user_id = UUID(user_id_str)
            except ValueError:
                logger.warning(f"Invalid user ID format: {user_id_str}")
                return None
            
            # Get user from database
            user = await user_repository.get_by_id(user_id)
            
            if not user:
                logger.warning(f"User not found: {user_id}")
                return None
            
            # Verify user is active
            if not user.is_active:
                logger.warning(f"User is deactivated: {user_id}")
                return None
            
            logger.debug(f"Successfully authenticated user: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None


# Global authentication middleware instance
_auth_middleware: Optional[AuthenticationMiddleware] = None


def get_auth_middleware() -> AuthenticationMiddleware:
    """Get or create authentication middleware instance"""
    global _auth_middleware
    
    if _auth_middleware is None:
        _auth_middleware = AuthenticationMiddleware()
    
    return _auth_middleware


# Convenience dependency functions
async def get_current_user_optional(
    auth_middleware: AuthenticationMiddleware = Depends(get_auth_middleware),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository)
) -> Optional[User]:
    """Dependency to get current user (optional)"""
    return await auth_middleware.get_current_user_optional(credentials, user_repository)


async def get_current_user(
    auth_middleware: AuthenticationMiddleware = Depends(get_auth_middleware),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository)
) -> User:
    """Dependency to get current user (required)"""
    return await auth_middleware.get_current_user(credentials, user_repository)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to get current admin user"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user


async def get_current_manager_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to get current manager user"""
    if not current_user.is_manager():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager privileges required"
        )
    
    return current_user